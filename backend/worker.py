from app.celery_app import celery
from app.core.logging import setup_logging

# 1. Initialize Structured Logging
# We do this immediately so that worker startup logs (connection to Redis, etc.)
# are formatted as JSON, consistent with the API logs.
setup_logging(log_level="INFO")

# 2. Expose the Celery Application
# The Celery CLI will load this module and look for the 'celery' object.
# Command: celery -A app.worker worker --loglevel=info
celery = celery