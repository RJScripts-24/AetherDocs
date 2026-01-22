import logging
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.storage.local import LocalStorageManager
from app.services.storage.redis import RedisClient
from app.tasks.cleanup import purge_session

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start")
async def start_session():
    """
    Initializes a new ephemeral workspace.
    """
    session_id = uuid.uuid4()
    logger.info(f"Starting new session: {session_id}")
    
    try:
        # 1. Init File System
        storage = LocalStorageManager()
        storage.initialize_session(session_id)
        
        # 2. Init Redis State
        redis = RedisClient()
        await redis.set_session_ttl(session_id)
        await redis.close()
        
        return {"session_id": str(session_id), "status": "active"}

    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail="Could not initialize workspace")

@router.post("/{session_id}/revoke")
async def revoke_session(session_id: uuid.UUID, background_tasks: BackgroundTasks):
    """
    Triggers the 'Burner' protocol to wipe all data.
    """
    logger.info(f"Revoke requested for: {session_id}")
    
    # We use a background task via Celery for reliability, 
    # but since purge_session is a Celery task, we call .delay()
    purge_session.delay(str(session_id))
    
    return {"message": "Session revocation scheduled", "status": "revoked"}
