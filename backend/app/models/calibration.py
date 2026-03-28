from pydantic import BaseModel, Field
from typing import Literal


class CalibrationStartRequest(BaseModel):
    user_id: str = Field(..., description="캘리브레이션 대상 사용자 ID")


class CalibrationStepRequest(BaseModel):
    zone_name: Literal["door", "toilet", "sink"] = Field(..., description="현재 진행할 존 이름")


class CalibrationCompleteRequest(BaseModel):
    zone_name: Literal["door", "toilet", "sink"] = Field(..., description="완료 처리할 존 이름")