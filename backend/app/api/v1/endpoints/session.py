from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
async def start_session():
    return {"message": "Session started"}

@router.post("/revoke")
async def revoke_session():
    return {"message": "Session revoked"}
