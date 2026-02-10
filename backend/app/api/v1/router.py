from fastapi import APIRouter
from app.api.v1.endpoints import session, upload, chat, status, download

api_router = APIRouter()
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(download.router, prefix="/download", tags=["download"])
