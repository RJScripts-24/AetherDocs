import asyncio
import httpx
import logging
import time
import uuid
import random
from typing import List

# Configuration
API_URL = "http://localhost:8000/api/v1"
CONCURRENT_USERS = 5  # Start small, increase to 20+ to test limits
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # "Me at the zoo" (Short, 19s video)

# Setup Logger
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)

async def simulate_user(client: httpx.AsyncClient, user_id: int):
    """
    Simulates a single user's journey through AetherDocs.
    """
    try:
        # 1. Start Session
        start_time = time.time()
        response = await client.post(f"{API_URL}/sessions/start", json={"ttl_seconds": 300})
        
        if response.status_code != 200:
            logger.error(f"[User {user_id}] Failed to start session: {response.text}")
            return
            
        session_data = response.json()
        session_id = session_data["session_id"]
        logger.info(f"[User {user_id}] Session started: {session_id}")

        # 2. Submit YouTube URL (Ingestion)
        # We add a small random delay so not all requests hit exactly at once
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        ingest_payload = {
            "session_id": session_id,
            "url": TEST_VIDEO_URL
        }
        resp = await client.post(f"{API_URL}/ingest/youtube", json=ingest_payload)
        if resp.status_code != 202:
            logger.error(f"[User {user_id}] Ingestion failed: {resp.text}")
            return

        # 3. Trigger Synthesis
        trigger_payload = {
            "session_id": session_id,
            "mode": "fast" # Use fast mode for stress testing
        }
        await client.post(f"{API_URL}/ingest/process", json=trigger_payload)
        logger.info(f"[User {user_id}] Pipeline triggered.")

        # 4. Poll for Status (Busy Wait)
        status = "queued"
        attempts = 0
        max_attempts = 60 # 2 minutes max for a 19s video
        
        while status not in ["completed", "failed"] and attempts < max_attempts:
            await asyncio.sleep(2)
            status_resp = await client.get(f"{API_URL}/sessions/{session_id}/status")
            if status_resp.status_code == 200:
                data = status_resp.json()
                status = data["status"]
                # logger.debug(f"[User {user_id}] Status: {status} ({data.get('progress_percentage')}%)")
            attempts += 1

        if status == "completed":
            duration = time.time() - start_time
            logger.info(f"[User {user_id}] ✅ SUCCESS! Workflow finished in {duration:.2f}s")
        else:
            logger.error(f"[User {user_id}] ❌ FAILED or TIMED OUT. Final status: {status}")

        # 5. Cleanup (Revoke Session)
        await client.post(f"{API_URL}/sessions/revoke", json={"session_id": session_id})
        logger.info(f"[User {user_id}] Session revoked.")

    except Exception as e:
        logger.error(f"[User {user_id}] Exception: {e}")

async def main():
    logger.info(f"--- Starting Stress Test with {CONCURRENT_USERS} users ---")
    logger.info(f"Target URL: {API_URL}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [simulate_user(client, i) for i in range(CONCURRENT_USERS)]
        await asyncio.gather(*tasks)
    
    logger.info("--- Stress Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())