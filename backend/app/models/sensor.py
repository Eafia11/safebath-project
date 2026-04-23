from typing import Literal, Optional

from pydantic import BaseModel, Field


class MmWaveSensorRequest(BaseModel):
    detected: bool = Field(..., description="Occupancy detection flag.")
    x: Optional[float] = Field(None, description="Observed x coordinate.")
    y: Optional[float] = Field(None, description="Observed y coordinate.")
    z: Optional[float] = Field(None, description="Observed z coordinate / height.")
    motion_level: Optional[float] = Field(None, description="Motion intensity from the sensor.")
    velocity: Optional[float] = Field(None, description="Optional pre-computed velocity.")
    zone: Optional[str] = Field(None, description="Explicit zone label if already known.")
    still_time: Optional[int] = Field(None, description="Seconds without movement.")


class DoorSensorRequest(BaseModel):
    door_state: Literal["open", "closed"] = Field(..., description="Door state.")
