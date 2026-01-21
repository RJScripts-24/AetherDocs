from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class SessionStatus(str, Enum):
    """
    The master lifecycle states of a 'Burner' session.
    """
    ACTIVE = "active"           # Session is live, data exists in /tmp and Memory
    PROCESSING = "processing"   # Currently running ingestion/synthesis tasks
    READY = "ready"             # "Common Book" is generated, Chat is active
    EXPIRED = "expired"         # TTL Reached, soft delete pending
    REVOKED = "revoked"         # User triggered "Revoke Session" (Kill Switch)
    TERMINATED = "terminated"   # Data cryptographically wiped

class SessionCreateRequest(BaseModel):
    """
    Payload for the initial handshake (POST /start).
    Does NOT require user credentials (anonymous access).
    """
    client_fingerprint: Optional[str] = Field(
        None, 
        description="Optional browser fingerprint for rate limiting (hashed)"
    )
    # Allows user to set a custom TTL, defaulted to standard session limit (e.g., 2 hours)
    ttl_seconds: int = Field(
        default=7200, 
        ge=300, 
        le=86400, 
        description="Time-to-live for the session in seconds (Default: 2 hours)"
    )

class SessionResponse(BaseModel):
    """
    Response returned when a session is initialized.
    Contains the critical Session_UUID used for all subsequent requests.
    """
    session_id: UUID = Field(..., description="The ephemeral unique identifier")
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    
    # Paths are internal, but we return a resource URL for the frontend to confirm readiness
    workspace_ready: bool = Field(False, description="True if /tmp workspace is allocated")

class RevokeSessionRequest(BaseModel):
    """
    Payload for the Kill Switch (POST /revoke).
    """
    session_id: UUID = Field(..., description="The session to destroy immediately")
    reason: Optional[str] = Field(
        "user_request", 
        description="Reason for termination (user_request, timeout, error)"
    )