import logging
import asyncio
from uuid import UUID

from app.celery_app import celery
from app.services.storage.local import LocalStorageManager
from app.services.storage.redis import RedisClient
from app.services.vector.db import VectorDBClient

# Setup logger
logger = logging.getLogger(__name__)

@celery.task(name="tasks.cleanup.purge_session")
def purge_session(session_id_str: str):
    """
    THE BURNER PROTOCOL.
    
    Triggered when:
    1. User clicks "Revoke Session"
    2. Session TTL expires
    3. Severe pipeline error occurs
    
    Actions:
    1. Wipe /tmp file system (Sync)
    2. Drop ChromaDB Collection (Sync)
    3. Flush Redis Keys (Async wrapper)
    """
    session_id = UUID(session_id_str)
    logger.info(f"[{session_id}] ⚠️ INITIATING BURNER PROTOCOL (CLEANUP) ...")

    # 1. Physical Storage Wipe
    try:
        storage = LocalStorageManager()
        success = storage.nuke_session(session_id)
        if success:
            logger.info(f"[{session_id}] ✓ File system wiped.")
        else:
            logger.warning(f"[{session_id}] File system wipe incomplete (dir might be missing).")
    except Exception as e:
        logger.error(f"[{session_id}] CRITICAL: Failed to wipe file system: {e}")

    # 2. Vector Brain Lobotomy
    try:
        vector_db = VectorDBClient()
        vector_db.delete_session_collection(session_id)
        logger.info(f"[{session_id}] ✓ Vector store deleted.")
    except Exception as e:
        logger.error(f"[{session_id}] Failed to delete vector collection: {e}")

    # 3. Redis Memory Flush
    # Since our RedisClient is async, we need to run it in an event loop
    try:
        asyncio.run(_async_redis_cleanup(session_id))
        logger.info(f"[{session_id}] ✓ Redis keys flushed.")
    except Exception as e:
        logger.error(f"[{session_id}] Failed to flush Redis: {e}")

    logger.info(f"[{session_id}] 🏁 SESSION DESTROYED. TRACES REMOVED.")

async def _async_redis_cleanup(session_id: UUID):
    """
    Helper to run async Redis operations inside the sync Celery task.
    """
    redis = RedisClient()
    try:
        await redis.flush_all_session_keys(session_id)
    finally:
        await redis.close()