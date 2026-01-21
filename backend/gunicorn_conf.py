import multiprocessing
import os

# --- Network Binding ---
# Bind to all interfaces (0.0.0.0) so it's accessible outside the Docker container
bind = os.getenv("BIND", "0.0.0.0:8000")

# --- Worker Configuration ---
# We use the Uvicorn worker class to support FastAPI's async nature
worker_class = "uvicorn.workers.UvicornWorker"

# Number of worker processes
# Formula: (2 x CPUs) + 1 is standard, but since we offload heavy
# AI tasks to Celery, the API layer is mostly I/O bound.
# We default to a sensible number or respect the WEB_CONCURRENCY env var.
cores = multiprocessing.cpu_count()
default_workers = (cores * 2) + 1
workers = int(os.getenv("WEB_CONCURRENCY", default_workers))

# --- Timeouts ---
# Standard is 30s. We increase this to 120s to allow for:
# 1. Large file uploads (500MB+ PDFs or Videos)
# 2. Slight delays during initial model loading (if not pre-warmed)
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# --- Logging ---
# '-' means log to stdout/stderr (essential for Docker logs)
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# --- Process Identity ---
proc_name = "aetherdocs_api"

# --- Advanced Tuning ---
# Preload app code before forking worker processes to save RAM
preload_app = True

# Max requests a worker will process before restarting
# (Helps prevent memory leaks in long-running Python processes)
max_requests = 1000
max_requests_jitter = 50