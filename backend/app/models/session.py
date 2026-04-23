from typing import Optional

from pydantic import BaseModel, Field


class SessionRecord(BaseModel):
    session_id: str = Field(..., description="Unique session identifier.")
    started_at: str = Field(..., description="Session start timestamp.")
    ended_at: Optional[str] = Field(None, description="Session end timestamp.")
    state: str = Field(default="ACTIVE", description="Current session state.")
