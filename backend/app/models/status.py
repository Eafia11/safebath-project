from typing import Optional

from pydantic import BaseModel, Field


class StatusSnapshot(BaseModel):
    current_state: str = Field(..., description="Current bathroom state.")
    last_door_state: Optional[str] = Field(None, description="Latest door sensor state.")
    last_mmwave_detected: bool = Field(..., description="Latest mmWave occupancy flag.")
    last_zone: Optional[str] = Field(None, description="Latest detected zone.")
    last_motion_level: Optional[float] = Field(None, description="Latest motion intensity.")
    last_still_time: Optional[int] = Field(None, description="Latest still-time value.")
    last_reason: str = Field(..., description="Reason for current state.")
    last_updated: Optional[str] = Field(None, description="Last state update timestamp.")
    waiting_for_response: bool = Field(..., description="Whether response confirmation is pending.")
    abnormal_start_time: Optional[str] = Field(
        None,
        description="Timestamp when abnormal inactivity started.",
    )
