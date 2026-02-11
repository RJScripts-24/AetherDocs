#!/bin/bash

# 1. Start Redis Server in the background
# We bind to 127.0.0.1 since everything is in the same container
echo "--- Starting Redis Server ---"
redis-server --daemonize yes

# 2. Start Celery Worker in the background
echo "--- Starting Celery Worker ---"
# using --concurrency 2 to avoid OOM on smaller instances, adjust if you have 16GB RAM
poetry run celery -A app.celery_app worker --loglevel=info --concurrency=2 &

# 3. Start FastAPI application
echo "--- Starting FastAPI on Port 7860 ---"
# Hugging Face Spaces expects the app to listen on port 7860
poetry run uvicorn main:app --host 0.0.0.0 --port 7860
