import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
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

@router.get("/{session_id}/metrics.json")
async def download_metrics(session_id: UUID):
    """
    Downloads the generated metrics.json artifact.
    """
    storage = LocalStorageManager()
    session_dir = storage._get_session_dir(session_id)
    metrics_path = session_dir / "artifacts" / "metrics.json"
    
    if not metrics_path.exists():
        # Check if synthesis completed but metrics weren't generated (old worker code)
        pdf_path = session_dir / "artifacts" / "CommonBook.pdf"
        if pdf_path.exists():
            # Pipeline completed but metrics.json wasn't written — return basic fallback
            logger.warning(f"[{session_id}] metrics.json missing but CommonBook.pdf exists. Returning fallback metrics.")
            return JSONResponse(content={
                "retrieval_accuracy": "N/A (Restart Celery worker for live metrics)",
                "answer_quality": "N/A",
                "processing_stats": {
                    "transcription_segments": 0,
                    "unique_insights": 0,
                    "topic_coverage": {}
                },
                "input_sources": {"files": [], "youtube_urls": []},
                "comparison_text": "Metrics unavailable — please restart the Celery worker and re-run synthesis for full metrics.",
                "ablation_text": "Metrics unavailable."
            })
        logger.error(f"[{session_id}] metrics.json not found at {metrics_path}")
        raise HTTPException(status_code=404, detail="Metrics not found. Synthesis may have failed.")
    
    return FileResponse(
        path=str(metrics_path),
        filename="metrics.json",
        media_type="application/json",
        content_disposition_type="inline"
    )
