import csv
from io import StringIO

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..core.security import verify_api_key
from ..models.common import success_response
from ..models.response import CommonResponse
from ..repositories.sensor_repository import sensor_repository
from ..services.alert_service import alert_service
from ..services.device_service import device_service
from ..services.log_service import log_service
from ..services.session_service import session_service
from ..services.state_service import state_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_api_key)])


@router.get("/snapshot", response_model=CommonResponse)
def get_admin_snapshot():
    active_session = session_service.get_active_session()
    return success_response(
        message="Admin snapshot retrieved successfully.",
        data={
            "status": state_service.get_status().model_dump(),
            "active_session": active_session.model_dump() if active_session else None,
            "devices": device_service.get_devices(),
            "alert_count": len(alert_service.get_alerts()),
            "log_count": len(log_service.get_logs()),
        },
    )


@router.get("/tuning", response_model=CommonResponse)
def get_tuning_records(limit: int = 100):
    records = _build_tuning_records(limit=limit)
    return success_response(
        message="Tuning records retrieved successfully.",
        data={"records": records},
    )


@router.get("/tuning.csv")
def download_tuning_csv(limit: int = 100):
    records = _build_tuning_records(limit=limit)
    fieldnames = [
        "id",
        "timestamp",
        "session_id",
        "detected",
        "x",
        "y",
        "z",
        "zone",
        "motion_level",
        "velocity",
        "still_time",
        "current_state",
        "waiting_for_response",
        "pending_response_type",
        "fall_detected",
        "fall_score",
        "height_drop",
        "speed_change",
        "anomaly_detected",
        "anomaly_score",
        "anomaly_reason",
    ]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=safebath_tuning.csv"},
    )


def _build_tuning_records(limit: int = 100) -> list[dict]:
    safe_limit = max(1, min(limit, 1000))
    records = sensor_repository.list_records(sensor="mmwave")[-safe_limit:]
    tuning_records = []
    for record in records:
        payload = record.get("payload") or {}
        status = record.get("status") or {}
        fall_detection = record.get("fall_detection") or {}
        anomaly = record.get("anomaly") or {}
        tuning_records.append(
            {
                "id": record.get("id"),
                "timestamp": record.get("timestamp"),
                "session_id": record.get("session_id"),
                "detected": payload.get("detected"),
                "x": payload.get("x"),
                "y": payload.get("y"),
                "z": payload.get("z"),
                "zone": payload.get("zone"),
                "motion_level": payload.get("motion_level"),
                "velocity": payload.get("velocity"),
                "still_time": payload.get("still_time"),
                "current_state": status.get("current_state"),
                "waiting_for_response": status.get("waiting_for_response"),
                "pending_response_type": status.get("pending_response_type"),
                "fall_detected": fall_detection.get("detected"),
                "fall_score": fall_detection.get("score"),
                "height_drop": fall_detection.get("height_drop"),
                "speed_change": fall_detection.get("speed_change"),
                "anomaly_detected": anomaly.get("detected"),
                "anomaly_score": anomaly.get("score"),
                "anomaly_reason": anomaly.get("reason"),
            }
        )
    return tuning_records
