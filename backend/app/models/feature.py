from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    detected: float = Field(..., description="Occupancy detection flag as 0/1.")
    motion_level: float = Field(0.0, description="Observed motion level.")
    still_time: float = Field(0.0, description="Seconds without movement.")
    zone_score: float = Field(0.0, description="Encoded zone weight.")
