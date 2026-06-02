from typing import Optional

from pydantic import BaseModel, Field


class StatusSnapshot(BaseModel):
    current_state: str = Field(..., description="Current bathroom state.")
    last_door_state: Optional[str] = Field(None, description="Latest door sensor state.")
    last_mmwave_detected: bool = Field(..., description="Latest mmWave occupancy flag.")
    last_mmwave_seen_at: Optional[str] = Field(
        None,
        description="Timestamp of the latest mmWave sample received by the backend.",
    )
    mmwave_online: bool = Field(
        False,
        description="Whether mmWave data has been received recently.",
    )
    last_zone: Optional[str] = Field(None, description="Latest detected zone.")
    last_motion_level: Optional[float] = Field(None, description="Latest motion intensity.")
    last_still_time: Optional[int] = Field(None, description="Latest still-time value.")
    last_reason: str = Field(..., description="Reason for current state.")
    last_updated: Optional[str] = Field(None, description="Last state update timestamp.")
    waiting_for_response: bool = Field(..., description="Whether response confirmation is pending.")
    pending_response_type: Optional[str] = Field(
        None,
        description="Type of pending user response, such as inactivity or fall.",
    )
    abnormal_start_time: Optional[str] = Field(
        None,
        description="Timestamp when abnormal inactivity started.",
    )
    last_fall_detected: bool = Field(
        False,
        description="Whether the latest mmWave sample matched fall rules.",
    )
    last_fall_score: float = Field(0.0, description="Rule-based fall confidence score.")
    last_fall_at: Optional[str] = Field(
        None,
        description="Timestamp of the latest detected fall event.",
    )
