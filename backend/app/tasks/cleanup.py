from app.celery_app import celery_app

@celery_app.task
def cleanup_temp_files():
    return "Cleanup complete"
