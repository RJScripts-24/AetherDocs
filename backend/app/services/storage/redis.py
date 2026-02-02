import logging
import json
from uuid import UUID
from typing import Optional, Any
from redis import asyncio as aioredis

from app.core.config import settings
from app.schemas.ingestion import IngestionStatus

# Setup logger
logger = logging.getLogger(__name__)

class RedisClient:
    """
    Async wrapper for Redis operations, handling session state and progress tracking.
    """

    def __init__(self):
        self.redis = aioredis.from_url(
            settings.REDIS_URL, 
            decode_responses=True
        )
        self.ttl_seconds = 3600 * 24  # 24 hours default TTL for session data

    async def close(self):
        """Closes the Redis connection."""
        await self.redis.close()

    async def update_progress(
        self, 
        session_id: UUID, 
        status: IngestionStatus, 
        percentage: int, 
        message: str,
        result_url: Optional[str] = None
    ):
        """
        Updates the granular progress of the ingestion pipeline.
        Data is stored as a hash: "session:{uuid}:status"
        """
        key = f"session:{session_id}:progress"
        
        payload = {
            "status": status.value,
            "progress_percentage": percentage,
            "current_step": message,
            "error_message": "" if status != IngestionStatus.FAILED else message
        }
        
        if result_url:
            payload["result_pdf_url"] = result_url

        try:
            # We store as a specific hash map or just a JSON string
            # JSON string is easier for simple polling
            await self.redis.set(key, json.dumps(payload), ex=self.ttl_seconds)
            
            # Also update a separate simple status key if needed for quick checks
            # await self.redis.hset(f"session:{session_id}", mapping={"status": status.value})
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to update Redis progress: {e}")

    async def get_progress(self, session_id: UUID) -> Optional[dict]:
        """
        Retrieves the current progress.
        """
        key = f"session:{session_id}:progress"
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"[{session_id}] Redis read error: {e}")
            return None

    async def set_session_ttl(self, session_id: UUID):
        """
        Creates or refreshes the session key with TTL.
        """
        key = f"session:{session_id}:progress"
        try:
            # Check if key exists, if not create initial state
            exists = await self.redis.exists(key)
            if not exists:
                initial_state = {
                    "status": "active",
                    "progress_percentage": 0,
                    "current_step": "Session initialized",
                    "error_message": ""
                }
                await self.redis.set(key, json.dumps(initial_state), ex=self.ttl_seconds)
            else:
                await self.redis.expire(key, self.ttl_seconds)
        except Exception as e:
            logger.error(f"[{session_id}] Failed to set session TTL: {e}")
            raise

    async def flush_all_session_keys(self, session_id: UUID):
        """
        Deletes all keys associated with a session.
        """
        pattern = f"session:{session_id}:*"
        
        try:
            # Dangerous in prod with huge datasets, but fine for separated session keys
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"[{session_id}] Deleted {len(keys)} Redis keys.")
        except Exception as e:
            logger.error(f"[{session_id}] Redis flush failed: {e}")
