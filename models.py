from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class SessionCreate(BaseModel):
    user_id: str

class EventLogCreate(BaseModel):
    session_id: UUID
    event_type: str
    content: str
    metadata: Optional[dict] = None

class SessionUpdate(BaseModel):
    end_time: datetime
    duration_seconds: int
    summary: str
    status: str

class WSMessage(BaseModel):
    type: str
    content: str
    metadata: Optional[dict] = None
