from fastapi import APIRouter
from datetime import datetime
from app.models.common import success_response
from app.models.response import CommonResponse
from app.models.sensor import MmWaveSensorRequest, DoorSensorRequest
from app.services.log_service import log_service
from app.services.state_service import state_service

router = APIRouter(prefix="/sensor", tags=["sensor"])


@router.post("/mmwave", response_model=CommonResponse)
def receive_mmwave(data: MmWaveSensorRequest):
    now = datetime.utcnow().isoformat()

    status = state_service.process_mmwave_event(
        detected=data.detected,
        zone=data.zone,
        motion_level=data.motion_level,
        still_time=data.still_time,
    )

    return success_response(
        message="mmWave 데이터 수신 완료",
        data={
            "timestamp": now,
            "received": True,
            "sensor": "mmwave",
            "payload": data.model_dump(),
            "status": status,
        }
    )


@router.post("/door", response_model=CommonResponse)
def receive_door(data: DoorSensorRequest):
    now = datetime.utcnow().isoformat()

    status = state_service.process_door_event(
        door_state=data.door_state
    )

    return success_response(
        message="도어 센서 데이터 수신 완료",
        data={
            "timestamp": now,
            "received": True,
            "sensor": "door",
            "payload": data.model_dump(),
            "status": status,
        }
    )