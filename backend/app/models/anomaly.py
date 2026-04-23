from typing import Optional

from pydantic import BaseModel, Field


class AnomalyPrediction(BaseModel):
    detected: bool = Field(..., description="Whether the sample is considered anomalous.")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized anomaly score.")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Current decision threshold.")
    reason: Optional[str] = Field(None, description="Human-readable explanation.")
    timestamp: Optional[str] = Field(None, description="Prediction timestamp.")
    source: Optional[str] = Field(None, description="Prediction source sensor.")
    current_state: Optional[str] = Field(None, description="State observed during prediction.")
