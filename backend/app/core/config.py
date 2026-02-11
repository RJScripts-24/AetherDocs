import os
import logging
import json
from pathlib import Path
from typing import Optional, Union, List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator

# --- Load .env BEFORE the Settings class is created ---
# This ensures os.getenv() calls in field defaults pick up
# the values from .env, and the Celery worker (which doesn't
# get --env-file like uvicorn) also has access to the env vars.
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

class Settings(BaseSettings):
    """
    Application Configuration.
    Reads from environment variables or .env file.
    """
    
    # --- Project Info ---
    PROJECT_NAME: str = "AetherDocs"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # --- Security & CORS ---
    # Union[List[str], str] allows pydantic-settings to accept a simple string from env vars,
    # avoiding the JSONDecodeError. The validator then parses it into a list.
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8000", "*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.strip().startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.strip().startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(",")
        return v

    # --- Infrastructure (Docker Service Names) ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))

    # --- Intelligence Keys ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # --- Security & Logging ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_to_a_secure_random_string")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # --- The "Burner" Storage ---
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/aether_workspace")
    
    # --- Model Caching ---
    WHISPER_CACHE_DIR: str = os.getenv("WHISPER_CACHE_DIR", "/app/models_cache/whisper")

    class Config:
        case_sensitive = True
        env_file = ".env"

# Instantiate global settings object
settings = Settings()

# Validation Check at Startup
if not settings.GROQ_API_KEY:
    logging.warning("⚠️ GROQ_API_KEY is missing! LLM synthesis features will fail.")