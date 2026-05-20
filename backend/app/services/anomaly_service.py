from ..detectors.anomaly_detector import anomaly_detector
from ..models.anomaly import AnomalyPrediction
from ..models.feature import FeatureVector
from ..models.status import StatusSnapshot
from ..repositories.anomaly_repository import anomaly_repository
from .alert_service import alert_service
from .log_service import log_service


class AnomalyService:
    def __init__(self):
        self.latest_prediction: AnomalyPrediction | None = None

    def analyze_mmwave(
        self,
        feature_vector: FeatureVector,
        status: StatusSnapshot,
        source: str = "mmwave",
    ) -> AnomalyPrediction:
        prediction = anomaly_detector.detect(
            feature_vector=feature_vector,
            status=status,
            source=source,
        )
        self.latest_prediction = prediction
        anomaly_repository.save(prediction)

        log_service.add_log(
            log_type="anomaly_service",
            message="Anomaly analysis completed",
            data=prediction.model_dump(),
            level="warning" if prediction.detected else "info",
        )

        if prediction.detected and status.current_state not in {"ABNORMAL", "EMERGENCY"}:
            created_alert = alert_service.create_alert(
                alert_type="anomaly",
                message="Anomalous behavior detected from mmWave data.",
                level="warning",
                target="guardian",
                data=prediction.model_dump(),
            )
            log_service.add_log(
                log_type="alert",
                message="Anomaly alert created from model prediction",
                data={"alert": created_alert.model_dump()},
                level="warning",
            )

        return prediction

    def get_latest_prediction(self) -> AnomalyPrediction | None:
        return self.latest_prediction


anomaly_service = AnomalyService()
