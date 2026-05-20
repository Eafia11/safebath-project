from typing import Iterable

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from .feature_pipeline import FEATURE_NAMES, features_to_matrix
from ..models.feature import FeatureVector
from ..utils.file_utils import ensure_parent_dir


class IsolationForestAnomalyModel:
    def __init__(
        self,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.random_state = random_state
        self.model: IsolationForest | None = None
        self.sample_count = 0
        self.raw_score_min = 0.0
        self.raw_score_max = 1.0

    def train(self, samples: Iterable[FeatureVector]):
        sample_list = list(samples)
        if not sample_list:
            self.model = None
            self.sample_count = 0
            return

        matrix = features_to_matrix(sample_list)
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )
        self.model.fit(matrix)
        raw_scores = self._raw_anomaly_scores(matrix)
        self.raw_score_min = float(np.min(raw_scores))
        self.raw_score_max = float(np.max(raw_scores))
        self.sample_count = len(sample_list)

    def is_trained(self) -> bool:
        return self.model is not None

    def score(self, sample: FeatureVector) -> float:
        if not self.model:
            return 0.0

        matrix = features_to_matrix([sample])
        raw_score = float(self._raw_anomaly_scores(matrix)[0])
        score_range = self.raw_score_max - self.raw_score_min
        if score_range <= 0:
            return 0.5
        return round(float(np.clip((raw_score - self.raw_score_min) / score_range, 0.0, 1.0)), 4)

    def is_anomaly(self, sample: FeatureVector) -> bool:
        if not self.model:
            return False
        prediction = int(self.model.predict(features_to_matrix([sample]))[0])
        return prediction == -1

    def save(self, path: str):
        if not self.model:
            return

        ensure_parent_dir(path)
        joblib.dump(
            {
                "model": self.model,
                "sample_count": self.sample_count,
                "raw_score_min": self.raw_score_min,
                "raw_score_max": self.raw_score_max,
                "contamination": self.contamination,
                "random_state": self.random_state,
                "feature_names": FEATURE_NAMES,
            },
            path,
        )

    def load(self, path: str):
        payload = joblib.load(path)
        self.model = payload["model"]
        self.sample_count = payload.get("sample_count", 0)
        self.raw_score_min = payload.get("raw_score_min", 0.0)
        self.raw_score_max = payload.get("raw_score_max", 1.0)
        self.contamination = payload.get("contamination", self.contamination)
        self.random_state = payload.get("random_state", self.random_state)

    def _raw_anomaly_scores(self, matrix: np.ndarray) -> np.ndarray:
        if not self.model:
            return np.zeros(matrix.shape[0])
        return -self.model.decision_function(matrix)
