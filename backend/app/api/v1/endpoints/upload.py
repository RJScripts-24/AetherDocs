from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def upload_file():
    return {"message": "File uploaded"}

@router.post("/youtube")
async def upload_youtube():
    return {"message": "YouTube video processed"}
