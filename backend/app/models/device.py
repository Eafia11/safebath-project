from typing import Literal, Optional

from pydantic import BaseModel, Field


class ButtonRequest(BaseModel):
    button_type: Literal["confirm_safe", "emergency_call", "reset"] = Field(
        ...,
        description="Button input type.",
    )


class SpeakerRequest(BaseModel):
    message: str = Field(..., description="Message to be played on the speaker.")
    alert_level: Literal["info", "warning", "danger"] = Field(
        ...,
        description="Speaker alert severity.",
    )
    repeat: Optional[int] = Field(1, ge=1, description="Number of times to repeat playback.")


class HeartbeatRequest(BaseModel):
    device_name: Literal["mmwave", "door_sensor", "button", "speaker"] = Field(
        ...,
        description="Device sending the heartbeat.",
    )
    status: Literal["online", "offline", "degraded"] = Field(
        default="online",
        description="Reported device connectivity status.",
    )


class DeviceState(BaseModel):
    device_name: str = Field(..., description="Device identifier.")
    status: str = Field(..., description="Current device status.")
    last_seen_at: Optional[str] = Field(None, description="Last heartbeat timestamp.")
    last_payload: Optional[dict] = Field(None, description="Most recent device payload.")
