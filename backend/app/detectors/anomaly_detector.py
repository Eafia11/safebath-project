from datetime import datetime

from ..models.anomaly import AnomalyPrediction
from ..models.feature import FeatureVector
from ..models.status import StatusSnapshot
from ..services.model_service import model_service


class AnomalyDetector:
    def detect(
        self,
        feature_vector: FeatureVector,
        status: StatusSnapshot,
        source: str = "mmwave",
    ) -> AnomalyPrediction:
        score = model_service.score(feature_vector)
        threshold = model_service.threshold
        detected = model_service.is_anomaly(feature_vector) or status.current_state in {
            "ABNORMAL",
            "EMERGENCY",
        }

        if status.current_state == "EMERGENCY":
            reason = "Emergency state is active."
        elif status.current_state == "ABNORMAL":
            reason = "Rule-based abnormal state is active."
        elif model_service.is_anomaly(feature_vector):
            reason = "Isolation Forest detected an anomalous sample."
        else:
            reason = "Score is within normal range."

        return AnomalyPrediction(
            detected=detected,
            score=round(score, 4),
            threshold=round(threshold, 4),
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
            source=source,
            current_state=status.current_state,
        )


anomaly_detector = AnomalyDetector()
