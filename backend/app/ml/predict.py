from ..models.feature import FeatureVector
from ..services.anomaly_service import anomaly_service
from ..services.model_service import model_service
from ..services.state_service import state_service


def predict_anomaly(raw_sample: dict):
    sample = FeatureVector(
        detected=float(bool(raw_sample.get("detected", False))),
        motion_level=float(raw_sample.get("motion_level", 0.0) or 0.0),
        still_time=float(raw_sample.get("still_time", 0.0) or 0.0),
        zone_score=float(raw_sample.get("zone_score", 0.0) or 0.0),
    )
    status = state_service.get_status()
    model_service.score(sample)
    return anomaly_service.analyze_mmwave(
        feature_vector=sample,
        status=status,
        source=raw_sample.get("source", "predict"),
    )
