import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def set_progress(task_id: str, progress: int):
    redis_client.set(f"task:{task_id}:progress", progress, ex=3600)
    
def get_progress(task_id: str):
    return redis_client.get(f"task:{task_id}:progress")
