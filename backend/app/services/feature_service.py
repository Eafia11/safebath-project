from ..models.feature import FeatureVector
from ..models.sensor import MmWaveSensorRequest


class FeatureService:
    def _zone_score(self, zone: str | None) -> float:
        mapping = {
            "door": 0.2,
            "sink": 0.4,
            "toilet": 0.8,
        }
        return mapping.get(zone or "", 0.0)

    def build_mmwave_feature_vector(self, data: MmWaveSensorRequest) -> FeatureVector:
        return FeatureVector(
            detected=float(data.detected),
            motion_level=float(data.motion_level or 0.0),
            still_time=float(data.still_time or 0.0),
            zone_score=self._zone_score(data.zone),
        )


feature_service = FeatureService()
