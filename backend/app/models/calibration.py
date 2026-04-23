from typing import Literal, Optional

from pydantic import BaseModel, Field


class CalibrationStartRequest(BaseModel):
    user_id: str = Field(..., description="Calibration owner identifier.")


class CalibrationStepRequest(BaseModel):
    zone_name: Literal["door", "toilet", "sink"] = Field(
        ...,
        description="Zone currently being calibrated.",
    )


class CalibrationCompleteRequest(BaseModel):
    zone_name: Literal["door", "toilet", "sink"] = Field(
        ...,
        description="Zone whose calibration is being completed.",
    )
    center_x: Optional[float] = Field(None, description="Calibrated zone center x coordinate.")
    center_y: Optional[float] = Field(None, description="Calibrated zone center y coordinate.")
    radius: Optional[float] = Field(None, gt=0, description="Calibrated zone radius.")
