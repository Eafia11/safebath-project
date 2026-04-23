from typing import Any, Dict

from pydantic import BaseModel, Field


class AlertEvent(BaseModel):
    id: int = Field(..., description="Alert identifier.")
    timestamp: str = Field(..., description="Alert creation timestamp.")
    type: str = Field(..., description="Alert category.")
    level: str = Field(..., description="Alert severity level.")
    target: str = Field(..., description="Alert recipient target.")
    message: str = Field(..., description="Alert message.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Extra alert payload.")
    status: str = Field(default="created", description="Alert lifecycle status.")
