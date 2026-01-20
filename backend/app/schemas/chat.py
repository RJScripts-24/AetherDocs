from pydantic import BaseModel
from typing import List, Optional

class ChatQuery(BaseModel):
    question: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    citations: Optional[List[str]] = []
