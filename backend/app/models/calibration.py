from typing import Literal, Optional

from pydantic import BaseModel, Field


class CalibrationStartRequest(BaseModel):
    user_id: str = Field(..., description="Calibration owner identifier.")


class CalibrationStepRequest(BaseModel):
    zone_name: Literal["toilet", "sink", "bath"] = Field(
        ...,
        description="Zone currently being calibrated.",
    )


class CalibrationCompleteRequest(BaseModel):
    zone_name: Literal["toilet", "sink", "bath"] = Field(
        ...,
        description="Zone whose calibration is being completed.",
    )
    center_x: Optional[float] = Field(None, description="Calibrated zone center x coordinate.")
    center_y: Optional[float] = Field(None, description="Calibrated zone center y coordinate.")
    radius: Optional[float] = Field(None, gt=0, description="Calibrated zone radius.")
    sample_limit: int = Field(
        20,
        ge=1,
        le=200,
        description="Number of recent mmWave samples to use when center coordinates are omitted.",
    )
    min_samples: int = Field(
        5,
        ge=1,
        le=50,
        description="Minimum valid samples required for automatic calibration.",
    )
    radius_padding: float = Field(
        0.05,
        ge=0.0,
        le=1.0,
        description="Extra radius added around the sampled coordinate spread.",
    )
