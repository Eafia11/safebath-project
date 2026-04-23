from typing import Optional

from pydantic import BaseModel, Field


class SessionRecord(BaseModel):
    session_id: str = Field(..., description="Unique session identifier.")
    started_at: str = Field(..., description="Session start timestamp.")
    ended_at: Optional[str] = Field(None, description="Session end timestamp.")
    state: str = Field(default="ACTIVE", description="Current session state.")
    start_zone: Optional[str] = Field(None, description="Zone observed when the session started.")
    last_zone: Optional[str] = Field(None, description="Most recent observed zone during the session.")
    event_count: int = Field(0, description="Number of sensor events linked to the session.")
    duration_seconds: Optional[float] = Field(None, description="Completed session duration in seconds.")
