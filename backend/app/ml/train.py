from typing import Iterable, List

from ..models.feature import FeatureVector
from ..services.model_service import model_service


def build_training_samples(raw_samples: Iterable[dict]) -> List[FeatureVector]:
    samples: List[FeatureVector] = []
    for raw in raw_samples:
        samples.append(
            FeatureVector(
                detected=float(bool(raw.get("detected", False))),
                motion_level=float(raw.get("motion_level", 0.0) or 0.0),
                still_time=float(raw.get("still_time", 0.0) or 0.0),
                zone_score=float(raw.get("zone_score", 0.0) or 0.0),
            )
        )
    return samples


def train_model(raw_samples: Iterable[dict]):
    samples = build_training_samples(raw_samples)
    return model_service.train(samples)
