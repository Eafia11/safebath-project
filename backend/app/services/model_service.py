from statistics import mean
from typing import Iterable, Optional

from ..core.config import MODEL_PATH
from ..ml.isolation_forest import IsolationForestAnomalyModel
from ..models.feature import FeatureVector
from ..utils.time_utils import utc_now_iso


class ModelService:
    def __init__(self):
        self.threshold = 0.7
        self.last_trained_at: Optional[str] = None
        self.sample_count = 0
        self.average_motion_level = 0.0
        self.model_path = MODEL_PATH
        self.isolation_forest = IsolationForestAnomalyModel()

    def train(self, samples: Iterable[FeatureVector]):
        sample_list = list(samples)
        self.sample_count = len(sample_list)
        self.average_motion_level = (
            mean(sample.motion_level for sample in sample_list) if sample_list else 0.0
        )
        self.isolation_forest.train(sample_list)
        self.isolation_forest.save(self.model_path)
        self.last_trained_at = utc_now_iso()
        return self.get_metadata()

    def score(self, sample: FeatureVector) -> float:
        if self.isolation_forest.is_trained():
            return self.isolation_forest.score(sample)

        return self._heuristic_score(sample)

    def is_anomaly(self, sample: FeatureVector) -> bool:
        if self.isolation_forest.is_trained():
            return self.isolation_forest.is_anomaly(sample)

        return self._heuristic_score(sample) >= self.threshold

    def load_model(self):
        self.isolation_forest.load(self.model_path)
        self.sample_count = self.isolation_forest.sample_count
        return self.get_metadata()

    def _heuristic_score(self, sample: FeatureVector) -> float:
        motion_delta = abs(sample.motion_level - self.average_motion_level)
        still_component = min(sample.still_time / 60.0, 1.0)
        detected_component = 0.2 if sample.detected else 0.0
        velocity_component = min(sample.velocity / 2.0, 1.0) * 0.15
        distance_component = min(sample.distance_from_origin / 5.0, 1.0) * 0.05
        zone_component = min(sample.zone_score, 1.0) * 0.1
        return min(
            round(
                motion_delta
                + still_component
                + detected_component
                + velocity_component
                + distance_component
                + zone_component,
                4,
            ),
            1.0,
        )

    def get_metadata(self):
        return {
            "threshold": self.threshold,
            "sample_count": self.sample_count,
            "average_motion_level": round(self.average_motion_level, 4),
            "last_trained_at": self.last_trained_at,
            "model_type": "IsolationForest",
            "model_path": self.model_path,
            "is_trained": self.isolation_forest.is_trained(),
        }


model_service = ModelService()
