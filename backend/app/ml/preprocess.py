from typing import Iterable, List

import pandas as pd

from ..models.feature import FeatureVector
from ..utils.math_utils import distance_2d, safe_float


def _zone_score(zone: str | None) -> float:
    mapping = {
        "sink": 0.4,
        "bath": 0.6,
        "toilet": 0.8,
    }
    return mapping.get(zone or "", 0.0)


def _zone_flag(zone: str | None, target_zone: str) -> float:
    return 1.0 if zone == target_zone else 0.0


def raw_sample_to_feature(raw_sample: dict) -> FeatureVector:
    x = safe_float(raw_sample.get("x"))
    y = safe_float(raw_sample.get("y"))
    z = safe_float(raw_sample.get("z"))
    zone = raw_sample.get("zone")
    return FeatureVector(
        detected=float(bool(raw_sample.get("detected", False))),
        x=x,
        y=y,
        z=z,
        motion_level=safe_float(raw_sample.get("motion_level")),
        velocity=safe_float(raw_sample.get("velocity")),
        still_time=safe_float(raw_sample.get("still_time")),
        distance_from_origin=safe_float(
            raw_sample.get("distance_from_origin"),
            default=distance_2d(x, y, 0.0, 0.0),
        ),
        zone_score=safe_float(raw_sample.get("zone_score"), default=_zone_score(zone)),
        is_door_zone=safe_float(raw_sample.get("is_door_zone"), default=_zone_flag(zone, "door")),
        is_sink_zone=safe_float(raw_sample.get("is_sink_zone"), default=_zone_flag(zone, "sink")),
        is_toilet_zone=safe_float(
            raw_sample.get("is_toilet_zone"),
            default=_zone_flag(zone, "toilet"),
        ),
    )


def build_training_samples(raw_samples: Iterable[dict]) -> List[FeatureVector]:
    return [raw_sample_to_feature(raw_sample) for raw_sample in raw_samples]


def load_training_samples_from_csv(csv_path: str) -> List[FeatureVector]:
    frame = pd.read_csv(csv_path)
    return build_training_samples(frame.to_dict(orient="records"))
