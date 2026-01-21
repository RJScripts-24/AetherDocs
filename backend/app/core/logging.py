import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs as JSON objects.
    Essential for production observability (Docker/CloudWatch/Datadog).
    """
    def format(self, record: logging.LogRecord) -> str:
        # Build the structured log dict
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Basic attempt to extract session_id if present in extra args
        # Usage: logger.info("msg", extra={"session_id": "..."})
        if hasattr(record, "session_id"):
            log_obj["session_id"] = record.session_id

        return json.dumps(log_obj)

def setup_logging(log_level: str = "INFO"):
    """
    Configures the root logger for the application.
    Call this once in main.py and worker.py startup.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers (e.g. from Uvicorn) to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Create Console Handler (Standard Output for Docker)
    handler = logging.StreamHandler(sys.stdout)
    
    # Apply JSON formatting
    # In local dev, you might prefer standard formatting, but JSON is safer for the specified stack
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    
    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    
    # Ensure Uvicorn uses our config
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]

# Helper to get logger in other modules
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)