from celery import Celery
from app.core.config import settings

# Initialize Celery
# Broker & Backend are both Redis in this architecture
celery = Celery(
    "aetherdocs",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    # Explicitly register the task modules so the worker finds them
    include=[
        "app.tasks.pipeline", 
        "app.tasks.cleanup"
    ]
)

# Apply configuration updates
celery.conf.update(
    # Serialization (Security best practice: restrict to JSON)
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    
    # Timezone settings
    timezone="UTC",
    enable_utc=True,

    # Optimization for long-running tasks (Video Transcription)
    # We allow tasks to be acknowledged only after completion (acks_late)
    # to prevent data loss if a worker crashes mid-transcription.
    task_acks_late=True,
    worker_prefetch_multiplier=1, # One task per worker at a time (Heavy AI load)
    
    # Safety Limits
    task_track_started=True,
    task_time_limit=3600,      # Hard kill after 1 hour
    task_soft_time_limit=3300, # Soft warning signal at 55 mins
)

if __name__ == "__main__":
    celery.start()