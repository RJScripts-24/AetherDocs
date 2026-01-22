import logging
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.services.storage.local import LocalStorageManager
from app.schemas.ingestion import FileUploadMetadata, SourceType, TriggerSynthesisRequest
from app.tasks.pipeline import run_ingestion_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=FileUploadMetadata)
async def upload_file(
    session_id: uuid.UUID = Form(...),
    file: UploadFile = File(...)
):
    """
    Accepts a file upload (PDF, DOCX, etc.) and saves it to the session's tmp folder.
    """
    logger.info(f"[{session_id}] Receiving file: {file.filename}")
    
    try:
        storage = LocalStorageManager()
        saved_path = await storage.save_upload(session_id, file)
        
        # Determine source type
        ext = saved_path.suffix.lower()
        source_type = SourceType.PDF # Default
        if ext in ['.mp3', '.wav']: source_type = SourceType.AUDIO
        elif ext in ['.mp4', '.mov']: source_type = SourceType.VIDEO
        elif ext == '.docx': source_type = SourceType.DOCX
        elif ext == '.pptx': source_type = SourceType.PPTX
        
        return FileUploadMetadata(
            file_id=file.filename,
            filename=file.filename,
            file_size_mb=round(saved_path.stat().st_size / (1024 * 1024), 2),
            source_type=source_type
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@router.post("/synthesize")
async def trigger_synthesis(payload: TriggerSynthesisRequest):
    """
    Triggers the 'Black Box' pipeline.
    """
    logger.info(f"[{payload.session_id}] Triggering synthesis (Mode: {payload.mode})")
    
    # Send to Celery
    # Note: run_ingestion_pipeline expects string args for UUID/Enums to be safe
    run_ingestion_pipeline.delay(
        str(payload.session_id), 
        payload.mode.value, 
        str(payload.youtube_url) if payload.youtube_url else None
    )
    
    return {"message": "Ingestion pipeline queued", "status": "queued"}
