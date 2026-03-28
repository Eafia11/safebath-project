from pydantic import BaseModel, Field
from typing import Optional, Literal


class MmWaveSensorRequest(BaseModel):
    detected: bool = Field(..., description="사용자 감지 여부")
    x: Optional[float] = Field(None, description="사용자 x 좌표")
    y: Optional[float] = Field(None, description="사용자 y 좌표")
    motion_level: Optional[float] = Field(None, description="움직임 정도")
    zone: Optional[str] = Field(None, description="감지 구역")
    still_time: Optional[int] = Field(None, description="정지 시간(초)")


class DoorSensorRequest(BaseModel):
    door_state: Literal["open", "closed"] = Field(..., description="문 상태")