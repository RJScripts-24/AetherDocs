#!/usr/bin/env bash

# Export PATH to ensure FFmpeg is found
export PATH="$HOME/ffmpeg_bin:$PATH"

# 1. Start Celery Worker in the background
echo "--- Starting Celery Worker ---"
celery -A worker worker --loglevel=info &

# 2. Start FastAPI via Gunicorn
echo "--- Starting FastAPI Server ---"
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
