import csv
from io import StringIO
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field

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


class DemoMmwaveRecord(BaseModel):
    timestamp: str
    detected: bool = False
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    zone: Optional[str] = None
    motion_level: float = 0.0
    velocity: float = 0.0
    still_time: int = 0
    current_state: str = "EMPTY"
    anomaly_detected: bool = False
    anomaly_score: float = 0.0
    anomaly_reason: Optional[str] = None
    fall_detected: bool = False
    fall_score: float = 0.0
    fall_reason: Optional[str] = None
    emergency_source: Optional[str] = None
    scenario: Optional[str] = None


class DemoMmwaveImportRequest(BaseModel):
    records: list[DemoMmwaveRecord] = Field(default_factory=list, max_length=20000)
    clear_existing: bool = False


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


@router.post("/demo/mmwave", response_model=CommonResponse)
def import_demo_mmwave_records(request: DemoMmwaveImportRequest):
    if request.clear_existing:
        sensor_repository.clear()

    imported = []
    for record in request.records:
        payload = {
            "detected": record.detected,
            "x": record.x,
            "y": record.y,
            "z": record.z,
            "zone": record.zone,
            "motion_level": record.motion_level,
            "velocity": record.velocity,
            "still_time": record.still_time,
            "scenario": record.scenario,
        }
        status = {
            "current_state": record.current_state,
            "last_zone": record.zone,
            "last_motion_level": record.motion_level,
            "last_still_time": record.still_time,
            "last_reason": record.anomaly_reason or record.fall_reason or "Imported demo record",
            "last_emergency_source": record.emergency_source,
        }
        anomaly = {
            "detected": record.anomaly_detected,
            "score": record.anomaly_score,
            "reason": record.anomaly_reason,
        }
        fall_detection = {
            "detected": record.fall_detected,
            "score": record.fall_score,
            "reason": record.fall_reason,
        }
        feature_vector = {
            "motion_level": record.motion_level,
            "velocity": record.velocity,
            "still_time": record.still_time,
            "zone": record.zone,
        }
        imported.append(
            sensor_repository.save_mmwave(
                timestamp=record.timestamp,
                payload=payload,
                feature_vector=feature_vector,
                anomaly=anomaly,
                fall_detection=fall_detection,
                status=status,
            )
        )

    timestamps = [record.timestamp for record in request.records]
    return success_response(
        message="Demo mmWave records imported successfully.",
        data={
            "imported_count": len(imported),
            "clear_existing": request.clear_existing,
            "period": {
                "start": min(timestamps) if timestamps else None,
                "end": max(timestamps) if timestamps else None,
            },
        },
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
