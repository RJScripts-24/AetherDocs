import logging
from typing import AsyncGenerator, Generator
from uuid import UUID
from fastapi import Depends, HTTPException, status, Path

from app.services.storage.redis import RedisClient
from app.services.vector.db import VectorDBClient
from app.schemas.session_state import SessionStatus

# Setup logger
logger = logging.getLogger(__name__)

async def get_redis() -> AsyncGenerator[RedisClient, None]:
    """
    Dependency that yields a RedisClient.
    Ensures the connection pool is properly closed after the request finishes.
    """
    client = RedisClient()
    try:
        yield client
    finally:
        await client.close()

def get_vector_db() -> Generator[VectorDBClient, None, None]:
    """
    Dependency that yields the VectorDBClient (ChromaDB wrapper).
    """
    client = VectorDBClient()
    try:
        yield client
    finally:
        # Chroma HTTP client doesn't strictly require a close(), 
        # but this block ensures extensibility if we switch to a stateful client later.
        pass

async def verify_active_session(
    session_id: UUID = Path(..., description="The Session UUID to validate"),
    redis: RedisClient = Depends(get_redis)
) -> UUID:
    """
    Critical Security Dependency.
    Checks if the requested Session ID exists in Redis and is not 'REVOKED'.
    
    Usage:
        def get_status(
            session_id: UUID = Depends(verify_active_session)
        ): ...
        
    Raises:
        404: If session expired/doesn't exist.
        403: If session was manually revoked.
    """
    session_status = await redis.get_session_status(session_id)
    
    if not session_status:
        logger.warning(f"Access attempted on missing/expired session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or has expired."
        )
        
    if session_status == SessionStatus.REVOKED:
        logger.warning(f"Access attempted on revoked session: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session has been revoked."
        )
    
    return session_id