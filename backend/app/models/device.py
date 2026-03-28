from pydantic import BaseModel, Field
from typing import Literal, Optional


class ButtonRequest(BaseModel):
    button_type: Literal["confirm_safe", "emergency_call", "reset"] = Field(
        ...,
        description="버튼 입력 종류"
    )


class SpeakerRequest(BaseModel):
    message: str = Field(..., description="스피커 출력 메시지")
    alert_level: Literal["info", "warning", "danger"] = Field(
        ...,
        description="안내/경고 수준"
    )
    repeat: Optional[int] = Field(1, description="반복 횟수")