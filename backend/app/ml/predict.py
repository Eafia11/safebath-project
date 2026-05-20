from .preprocess import raw_sample_to_feature
from ..services.anomaly_service import anomaly_service
from ..services.state_service import state_service


def predict_anomaly(raw_sample: dict):
    sample = raw_sample_to_feature(raw_sample)
    status = state_service.get_status()
    return anomaly_service.analyze_mmwave(
        feature_vector=sample,
        status=status,
        source=raw_sample.get("source", "predict"),
    )
