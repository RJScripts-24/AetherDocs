import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# Setup logger
# We configure it immediately so even startup errors are captured in JSON format
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown lifecycle of the application.
    """
    # --- Startup ---
    logger.info("--- AetherDocs System Starting ---")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Environment: Production" if not settings.GROQ_API_KEY.startswith("gsk_") else "Environment: Dev")
    
    # You could add a check here to verify Redis is reachable before accepting traffic
    # e.g., await redis.ping()
    
    yield
    
    # --- Shutdown ---
    logger.info("--- AetherDocs System Shutting Down ---")
    # Any global cleanup (closing HTTP clients, database pools) goes here.
    # Note: Dependency injection usually handles connection closing per request,
    # so we don't strictly need manual cleanup here for this specific stack.

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Ephemeral RAG Architecture for Automated Study Guide Generation",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- Security: CORS Middleware ---
# Controls which domains can talk to this API.
# Defined in config.py (default allows localhost:3000 for frontend)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Router Registration ---
# We mount all endpoints under /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple heartbeat endpoint for health monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.get("/", include_in_schema=False)
async def root():
    """
    Redirect root to docs or return basic info.
    """
    return {
        "message": "AetherDocs API is running. Visit /docs for Swagger UI."
    }