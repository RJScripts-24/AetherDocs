import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.services.storage.local import LocalStorageManager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{session_id}/commonbook")
async def download_commonbook(session_id: UUID):
    """
    Downloads the generated CommonBook.pdf artifact.
    """
    storage = LocalStorageManager()
    session_dir = storage._get_session_dir(session_id)
    pdf_path = session_dir / "artifacts" / "CommonBook.pdf"
    
    if not pdf_path.exists():
        logger.error(f"[{session_id}] CommonBook.pdf not found at {pdf_path}")
        raise HTTPException(status_code=404, detail="CommonBook PDF not found. Synthesis may have failed.")
    
    return FileResponse(
        path=str(pdf_path),
        filename="CommonBook.pdf",
        media_type="application/pdf",
        content_disposition_type="inline"
    )
