from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
async def query_chat():
    return {"message": "Query received"}
