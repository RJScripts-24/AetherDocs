import asyncio
import logging
from typing import List, Optional
import uuid
from uuid import UUID

from app.celery_app import celery
from app.schemas.ingestion import IntelligenceMode, IngestionStatus
from app.services.storage.local import LocalStorageManager
from app.services.storage.redis import RedisClient
from app.services.media.downloader import YouTubeDownloader
from app.services.media.transcriber import AudioTranscriber
from app.services.vision.pdf_parser import PDFParser
from app.services.vision.docx_parser import DocxParser
from app.services.vision.pptx_parser import PptxParser
from app.services.vector.chunker import SemanticChunker
from app.services.vector.db import VectorDBClient
from app.services.synthesis.generator import LLMClient
from app.services.synthesis.fusion import FusionEngine
from app.services.synthesis.pdf_writer import PDFGenerator

# Setup logger
logger = logging.getLogger(__name__)

@celery.task(bind=True, name="tasks.pipeline.run_ingestion")
def run_ingestion_pipeline(self, session_id_str: str, mode_str: str, youtube_url: Optional[str] = None):
    """
    The "Black Box" Pipeline.
    Executed by a Celery Worker (separate process from API).
    
    Workflow:
    1. Setup & Redis Handshake
    2. Media Ingestion (YouTube Download / File Loading)
    3. Intelligence Extraction (Whisper / Llama Vision)
    4. Vectorization (ChromaDB)
    5. Fusion & Synthesis (The "Smart Deduplication")
    6. PDF Artifact Generation
    """
    session_id = UUID(session_id_str)
    mode = IntelligenceMode(mode_str)
    
    # We run the async logic in a blocking call since Celery is sync
    try:
        asyncio.run(
            _execute_pipeline_async(session_id, mode, youtube_url)
        )
    except Exception as e:
        logger.critical(f"[{session_id}] Pipeline Crashed: {e}")
        # Final safety net to update Redis status to FAILED
        asyncio.run(_report_failure(session_id, str(e)))

async def _execute_pipeline_async(session_id: UUID, mode: IntelligenceMode, youtube_url: Optional[str]):
    """
    The actual logic, running in an async context.
    """
    redis = RedisClient()
    storage = LocalStorageManager()
    
    # --- PHASE 1: INITIALIZATION ---
    await redis.update_progress(session_id, IngestionStatus.QUEUED, 5, "Initializing workspace...")
    session_dir = storage.initialize_session(session_id)
    
    # Initialize Services
    transcriber = AudioTranscriber(model_size="large-v3" if mode == IntelligenceMode.DEEP else "distil-large-v3")
    pdf_parser = PDFParser()
    docx_parser = DocxParser()
    pptx_parser = PptxParser()
    chunker = SemanticChunker()
    vector_db = VectorDBClient()
    llm_client = LLMClient()
    fusion_engine = FusionEngine(llm_client)
    pdf_gen = PDFGenerator()

    # Collectors for raw data
    base_transcript_text = ""
    secondary_text_chunks = []
    
    try:
        # --- PHASE 2: MEDIA INGESTION (VIDEO) ---
        if youtube_url:
            await redis.update_progress(session_id, IngestionStatus.DOWNLOADING, 10, "Downloading Audio Stream...")
            downloader = YouTubeDownloader()
            # This is sync code (yt-dlp), but fast enough to run directly
            audio_path = downloader.download(youtube_url, session_dir / "uploads", session_id)
            
            await redis.update_progress(session_id, IngestionStatus.TRANSCRIBING, 20, "Transcribing Audio (Whisper)...")
            # Run Whisper
            transcript_segments = transcriber.transcribe(audio_path)
            base_transcript_text = transcriber.format_as_text(transcript_segments)
            
            # Vectorize the Transcript Segments directly to preserve timestamps
            # This is critical for "Strict Citations" [Video 12:45]
            video_chunks = []
            for seg in transcript_segments:
                # Group small segments if they are too short? 
                # Whisper segments are usually sentence-level, which is perfect for RAG.
                video_chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": seg["text"],
                    "metadata": {
                        "source": "video",
                        "type": "audio",
                        "timestamp": f"{int(seg['start']//60)}:{int(seg['start']%60):02d}", # "12:45" format
                        "start_seconds": seg['start'],
                        "end_seconds": seg['end']
                    }
                })
            
            if video_chunks:
                vector_db.add_documents(session_id, video_chunks)

        # --- PHASE 3: DOCUMENT PARSING (PDF/DOCX/PPTX) ---
        await redis.update_progress(session_id, IngestionStatus.OCR_PROCESSING, 40, "Reading Documents & Charts...")
        
        uploaded_files = storage.list_files(session_id, "uploads")
        
        for file_path in uploaded_files:
            ext = file_path.suffix.lower()
            file_chunks = []
            
            # Router
            if ext == ".pdf":
                file_chunks = await pdf_parser.parse(session_id, file_path, session_dir / "processed")
            elif ext == ".docx":
                file_chunks = await docx_parser.parse(session_id, file_path, session_dir / "processed")
            elif ext == ".pptx":
                file_chunks = await pptx_parser.parse(session_id, file_path, session_dir / "processed")
            else:
                continue # Skip non-document files (video/audio handled/skipped)
            
            # Vectorize
            for i, chunk_text in enumerate(file_chunks):
                # Chunking
                # We assume 1 chunk = 1 page/slide for PDF/PPTX from the parsers
                chunks = chunker.split_text(
                    chunk_text, 
                    source_metadata={
                        "source": file_path.name, 
                        "type": ext[1:],
                        "page": i + 1,
                        "source_id": f"{file_path.name}_p{i + 1}"
                    }
                )
                vector_db.add_documents(session_id, chunks)
                
                # Collect for Fusion Engine (Secondary Source)
                secondary_text_chunks.extend([c["text"] for c in chunks])

        # --- PHASE 4: SYNTHESIS (FUSION LOGIC) ---
        await redis.update_progress(session_id, IngestionStatus.SYNTHESIZING, 70, "Running Smart Deduplication...")
        
        if not base_transcript_text and not secondary_text_chunks:
            raise ValueError("No content found to synthesize! Please upload a PDF or Video.")

        # If only PDF provided, treat PDF as base. If only Video, treat Video as base.
        if not base_transcript_text:
            base_transcript_text = " ".join(secondary_text_chunks[:5]) # Hack: use first few pages as base
        
        final_manuscript = await fusion_engine.generate_common_book(
            session_id, 
            base_transcript_text, 
            secondary_text_chunks, 
            mode
        )

        # --- PHASE 5: ARTIFACT GENERATION ---
        await redis.update_progress(session_id, IngestionStatus.SYNTHESIZING, 90, "Generating PDF...")
        
        pdf_path = session_dir / "artifacts" / "CommonBook.pdf"
        pdf_gen.generate(session_id, final_manuscript, pdf_path)
        
        # --- COMPLETION ---
        # Generate a download URL (assuming API serves /downloads/{session_id}/artifacts/...)
        download_url = f"/api/v1/sessions/{session_id}/download"
        
        # Final update with the result link
        # We cheat and put the URL in the 'error_message' field or 'message' field if using a generic dict,
        # but here we update status to COMPLETED which signals frontend to check results.
        await redis.update_progress(session_id, IngestionStatus.COMPLETED, 100, "Ready")
        
        # Store result link in Redis separately if needed, or rely on convention
        # For this architecture, the Frontend just calls GET /download once status is COMPLETED.
        
        logger.info(f"[{session_id}] Pipeline Completed Successfully.")

    except Exception as e:
        logger.error(f"[{session_id}] Error in async pipeline: {e}")
        await redis.update_progress(session_id, IngestionStatus.FAILED, 0, str(e))
        raise e
    finally:
        await redis.close()

async def _report_failure(session_id: UUID, error: str):
    """Fallback error reporter."""
    redis = RedisClient()
    try:
        await redis.update_progress(session_id, IngestionStatus.FAILED, 0, error)
    finally:
        await redis.close()