from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.alert_service import alert_service
from ..services.anomaly_service import anomaly_service
from ..services.state_service import state_service

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=CommonResponse)
def get_anomalies():
    status = state_service.get_status()
    alerts = alert_service.get_alerts()
    latest_prediction = anomaly_service.get_latest_prediction()

    anomaly_state = (
        status.current_state in {"ABNORMAL", "EMERGENCY"}
        or (latest_prediction.detected if latest_prediction else False)
    )

    return success_response(
        message="Anomaly status retrieved successfully.",
        data={
            "detected": anomaly_state,
            "current_state": status.current_state,
            "current_zone": status.last_zone,
            "fall_detected": status.last_fall_detected,
            "fall_score": status.last_fall_score,
            "fall_detected_at": status.last_fall_at,
            "waiting_for_response": status.waiting_for_response,
            "latest_prediction": latest_prediction.model_dump() if latest_prediction else None,
            "latest_alert": alerts[-1].model_dump() if alerts else None,
            "alert_count": len(alerts),
        },
    )
