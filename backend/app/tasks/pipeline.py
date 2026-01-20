from app.celery_app import celery_app

@celery_app.task
def process_pipeline(file_path: str):
    return f"Processing {file_path}"
