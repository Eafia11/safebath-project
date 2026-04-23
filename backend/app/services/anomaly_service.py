from datetime import datetime

from ..models.anomaly import AnomalyPrediction
from ..models.feature import FeatureVector
from ..models.status import StatusSnapshot
from .alert_service import alert_service
from .log_service import log_service
from .model_service import model_service


class AnomalyService:
    def __init__(self):
        self.latest_prediction: AnomalyPrediction | None = None

    def analyze_mmwave(
        self,
        feature_vector: FeatureVector,
        status: StatusSnapshot,
        source: str = "mmwave",
    ) -> AnomalyPrediction:
        score = model_service.score(feature_vector)
        threshold = model_service.threshold
        detected = score >= threshold or status.current_state in {"ABNORMAL", "EMERGENCY"}

        if status.current_state == "EMERGENCY":
            reason = "Emergency state is active."
        elif status.current_state == "ABNORMAL":
            reason = "Rule-based abnormal state is active."
        elif score >= threshold:
            reason = "Score exceeded threshold."
        else:
            reason = "Score is within normal range."

        prediction = AnomalyPrediction(
            detected=detected,
            score=round(score, 4),
            threshold=round(threshold, 4),
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
            source=source,
            current_state=status.current_state,
        )
        self.latest_prediction = prediction

        log_service.add_log(
            log_type="anomaly_service",
            message="Anomaly analysis completed",
            data=prediction.model_dump(),
            level="warning" if detected else "info",
        )

        if detected and status.current_state not in {"ABNORMAL", "EMERGENCY"}:
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
