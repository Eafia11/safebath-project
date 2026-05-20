from typing import Any, Dict

from ..models.anomaly import AnomalyPrediction
from ..models.status import StatusSnapshot


class FusionDetector:
    def evaluate(
        self,
        *,
        fall_result: Dict[str, Any],
        anomaly_prediction: AnomalyPrediction,
        status: StatusSnapshot,
    ) -> Dict[str, Any]:
        if fall_result.get("detected"):
            return {
                "detected": True,
                "level": "danger",
                "reason": fall_result.get("reason"),
                "source": "fall_detector",
            }

        if status.current_state == "EMERGENCY":
            return {
                "detected": True,
                "level": "danger",
                "reason": status.last_reason,
                "source": "state_service",
            }

        if anomaly_prediction.detected:
            return {
                "detected": True,
                "level": "warning",
                "reason": anomaly_prediction.reason,
                "source": "anomaly_detector",
            }

        return {
            "detected": False,
            "level": "normal",
            "reason": "No fused risk detected.",
            "source": "fusion_detector",
        }


fusion_detector = FusionDetector()
