from typing import Iterable, List

import numpy as np

from ..models.feature import FeatureVector


FEATURE_NAMES = [
    "detected",
    "x",
    "y",
    "z",
    "motion_level",
    "velocity",
    "still_time",
    "distance_from_origin",
    "zone_score",
    "is_door_zone",
    "is_sink_zone",
    "is_toilet_zone",
]


def feature_to_row(feature_vector: FeatureVector) -> List[float]:
    return [
        feature_vector.detected,
        feature_vector.x,
        feature_vector.y,
        feature_vector.z,
        feature_vector.motion_level,
        feature_vector.velocity,
        feature_vector.still_time,
        feature_vector.distance_from_origin,
        feature_vector.zone_score,
        feature_vector.is_door_zone,
        feature_vector.is_sink_zone,
        feature_vector.is_toilet_zone,
    ]


def features_to_matrix(samples: Iterable[FeatureVector]) -> np.ndarray:
    return np.array([feature_to_row(sample) for sample in samples], dtype=float)
