from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: UUID = Field(..., description="The session to chat with")
    query: str = Field(..., description="User's question")
    history: Optional[List[Dict[str, str]]] = Field(
        default=[], 
        description="Previous conversation context [{'role': 'user', 'content': '...'}, ...]"
    )

class Citation(BaseModel):
    source_file: str
    page_number: Optional[int] = None
    timestamp: Optional[str] = None
    snippet: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]