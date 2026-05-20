from app.models.feature import FeatureVector
from app.models.status import StatusSnapshot
from app.services.anomaly_service import AnomalyService


def _status(current_state: str = "ACTIVE") -> StatusSnapshot:
    return StatusSnapshot(
        current_state=current_state,
        last_mmwave_detected=True,
        last_reason="test",
        waiting_for_response=False,
    )


def test_anomaly_service_detects_high_score_sample():
    service = AnomalyService()

    prediction = service.analyze_mmwave(
        feature_vector=FeatureVector(
            detected=1.0,
            motion_level=1.0,
            still_time=60.0,
            zone_score=0.8,
        ),
        status=_status(),
    )

    assert prediction.detected is True
    assert prediction.score >= prediction.threshold
    assert service.get_latest_prediction() == prediction


def test_anomaly_service_detects_abnormal_state_even_with_low_score():
    service = AnomalyService()

    prediction = service.analyze_mmwave(
        feature_vector=FeatureVector(
            detected=0.0,
            motion_level=0.0,
            still_time=0.0,
            zone_score=0.0,
        ),
        status=_status("ABNORMAL"),
    )

    assert prediction.detected is True
    assert prediction.current_state == "ABNORMAL"
