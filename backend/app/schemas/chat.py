from typing import List, Optional, Literal, Union
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

class Citation(BaseModel):
    """
    Represents a specific source reference used to generate an answer.
    Used by the frontend to create clickable links (e.g., jump to video timestamp).
    """
    source_file: str = Field(..., description="Name of the file (e.g., 'Lecture1.mp4')")
    source_type: Literal["pdf", "video", "audio", "image"] = Field(..., description="Type of media source")
    
    # Polymorphic location: A citation is either a page number (PDF) or a timestamp (Video/Audio)
    page_number: Optional[int] = Field(None, description="Page number for PDF documents")
    timestamp_seconds: Optional[float] = Field(None, description="Timestamp in seconds for Audio/Video")
    
    snippet: str = Field(..., description="The exact text chunk retrieved from the vector store")
    relevance_score: float = Field(..., description="Similarity score from ChromaDB (0-1)")

class ChatMessage(BaseModel):
    """
    A single message in the conversation history.
    """
    role: Literal["user", "assistant", "system"] = Field(..., description="Who sent the message")
    content: str = Field(..., description="The text content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatQueryRequest(BaseModel):
    """
    Payload sent by the user when asking a question.
    """
    session_id: UUID = Field(..., description="The active Session_UUID to query against")
    query: str = Field(..., min_length=1, description="The user's question")
    history: List[ChatMessage] = Field(
        default=[], 
        description="Previous conversation context to allow follow-up questions"
    )
    
    # Intelligence toggle
    mode: Literal["fast", "deep"] = Field(
        "fast", 
        description="Fast=Llama-3-8b (Speed), Deep=Llama-3-70b (Nuance)"
    )

class ChatQueryResponse(BaseModel):
    """
    The answer returned by the RAG engine.
    """
    answer: str = Field(..., description="The synthesized answer from the LLM")
    citations: List[Citation] = Field(
        default=[], 
        description="List of strict references used to construct the answer"
    )
    processing_time_ms: float = Field(..., description="Time taken to generate response")