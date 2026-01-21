from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, validator

class IntelligenceMode(str, Enum):
    """
    Defines the depth of analysis for the session.
    Matches the spec:
    - FAST: Llama-3-8b (Speed focus)
    - DEEP: Llama-3-70b (Nuance/Dense analysis focus)
    """
    FAST = "fast"
    DEEP = "deep"

class IngestionStatus(str, Enum):
    """
    Tracks the granular progress of the background pipeline.
    Used for the UI progress bar.
    """
    QUEUED = "queued"
    DOWNLOADING = "downloading"      # yt-dlp
    TRANSCRIBING = "transcribing"    # Whisper
    OCR_PROCESSING = "ocr_processing"# Llama Vision / PyMuPDF
    VECTORIZING = "vectorizing"      # ChromaDB embedding
    SYNTHESIZING = "synthesizing"    # Fusion Logic & PDF Gen
    COMPLETED = "completed"
    FAILED = "failed"

class SourceType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    VIDEO = "video"  # MP4, etc.
    AUDIO = "audio"  # MP3, WAV
    YOUTUBE = "youtube"

# --- Input Models ---

class YoutubeIngestRequest(BaseModel):
    """
    Payload for submitting a YouTube URL.
    """
    session_id: UUID = Field(..., description="The active Session UUID")
    url: HttpUrl = Field(..., description="Valid YouTube URL")

    @validator('url')
    def validate_youtube_url(cls, v):
        url_str = str(v)
        if "youtube.com" not in url_str and "youtu.be" not in url_str:
            raise ValueError("Must be a valid YouTube URL")
        return v

class FileUploadMetadata(BaseModel):
    """
    Metadata returned immediately after a file is uploaded to /tmp.
    Does NOT mean processing is done, just that the file is accepted.
    """
    file_id: str = Field(..., description="Unique ID for the uploaded file (filename or hash)")
    filename: str
    file_size_mb: float
    source_type: SourceType

# --- Trigger Models ---

class TriggerSynthesisRequest(BaseModel):
    """
    The 'Extract & Synthesize' button payload.
    Triggers the heavy async pipeline for all uploaded assets.
    """
    session_id: UUID = Field(..., description="The active Session UUID")
    mode: IntelligenceMode = Field(
        default=IntelligenceMode.FAST,
        description="Selects the model complexity (8b vs 70b)"
    )

# --- Status/Response Models ---

class PipelineProgressResponse(BaseModel):
    """
    Polled by the frontend to update the progress bar.
    """
    session_id: UUID
    status: IngestionStatus
    progress_percentage: int = Field(..., ge=0, le=100)
    current_step: str = Field(..., description="Human readable step e.g., 'Transcribing video (45%)...'")
    error_message: Optional[str] = None
    
    # populated only when status == COMPLETED
    result_pdf_url: Optional[str] = Field(None, description="Download link for the Common Book")