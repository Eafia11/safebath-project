from ..models.feature import FeatureVector
from ..models.sensor import MmWaveSensorRequest
from ..utils.math_utils import distance_2d


class FeatureService:
    def _zone_score(self, zone: str | None) -> float:
        mapping = {
            "sink": 0.4,
            "bath": 0.6,
            "toilet": 0.8,
        }
        return mapping.get(zone or "", 0.0)

    def _zone_flag(self, zone: str | None, target_zone: str) -> float:
        return 1.0 if zone == target_zone else 0.0

    def build_mmwave_feature_vector(self, data: MmWaveSensorRequest) -> FeatureVector:
        x = float(data.x or 0.0)
        y = float(data.y or 0.0)
        z = float(data.z or 0.0)
        return FeatureVector(
            detected=float(data.detected),
            x=x,
            y=y,
            z=z,
            motion_level=float(data.motion_level or 0.0),
            velocity=float(data.velocity or 0.0),
            still_time=float(data.still_time or 0.0),
            distance_from_origin=distance_2d(x, y, 0.0, 0.0),
            zone_score=self._zone_score(data.zone),
            is_door_zone=self._zone_flag(data.zone, "door"),
            is_sink_zone=self._zone_flag(data.zone, "sink"),
            is_toilet_zone=self._zone_flag(data.zone, "toilet"),
        )


feature_service = FeatureService()
