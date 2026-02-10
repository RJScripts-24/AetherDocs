import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.services.storage.redis import RedisClient

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{session_id}")
async def get_session_status(session_id: UUID):
    """
    Polls the current pipeline progress for a session.
    Frontend calls this every 1-2 seconds while synthesis is running.
    """
    redis = RedisClient()
    
    try:
        progress = await redis.get_progress(session_id)
        
        if not progress:
            return {
                "status": "active",
                "progress_percentage": 0,
                "current_step": "Waiting...",
                "error_message": ""
            }
        
        return progress
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis.close()
