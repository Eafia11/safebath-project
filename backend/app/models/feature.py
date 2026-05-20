from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    detected: float = Field(..., description="Occupancy detection flag as 0/1.")
    x: float = Field(0.0, description="Observed x coordinate.")
    y: float = Field(0.0, description="Observed y coordinate.")
    z: float = Field(0.0, description="Observed z coordinate / height.")
    motion_level: float = Field(0.0, description="Observed motion level.")
    velocity: float = Field(0.0, description="Observed or estimated movement velocity.")
    still_time: float = Field(0.0, description="Seconds without movement.")
    distance_from_origin: float = Field(0.0, description="Distance from the sensor origin.")
    zone_score: float = Field(0.0, description="Encoded zone weight.")
    is_door_zone: float = Field(0.0, description="Whether the sample belongs to the door zone.")
    is_sink_zone: float = Field(0.0, description="Whether the sample belongs to the sink zone.")
    is_toilet_zone: float = Field(0.0, description="Whether the sample belongs to the toilet zone.")
