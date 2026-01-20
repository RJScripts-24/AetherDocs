from fastapi import FastAPI
from app.api.v1.router import api_router
# from app.core.config import settings

app = FastAPI(title="AetherDocs API", version="0.1.0")

# Include router - commented out until router is created to allow running basic health check if needed immediately
# app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
