from datetime import datetime
from statistics import mean
from typing import Iterable, Optional

from ..models.feature import FeatureVector


class ModelService:
    def __init__(self):
        self.threshold = 0.7
        self.last_trained_at: Optional[str] = None
        self.sample_count = 0
        self.average_motion_level = 0.0

    def train(self, samples: Iterable[FeatureVector]):
        sample_list = list(samples)
        self.sample_count = len(sample_list)
        self.average_motion_level = (
            mean(sample.motion_level for sample in sample_list) if sample_list else 0.0
        )
        self.last_trained_at = datetime.utcnow().isoformat()
        return self.get_metadata()

    def score(self, sample: FeatureVector) -> float:
        motion_delta = abs(sample.motion_level - self.average_motion_level)
        still_component = min(sample.still_time / 60.0, 1.0)
        detected_component = 0.2 if sample.detected else 0.0
        zone_component = min(sample.zone_score, 1.0) * 0.1
        return min(
            round(motion_delta + still_component + detected_component + zone_component, 4),
            1.0,
        )

    def get_metadata(self):
        return {
            "threshold": self.threshold,
            "sample_count": self.sample_count,
            "average_motion_level": round(self.average_motion_level, 4),
            "last_trained_at": self.last_trained_at,
        }


model_service = ModelService()
