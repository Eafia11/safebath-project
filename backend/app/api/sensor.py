from datetime import datetime

from fastapi import APIRouter, Depends

from ..core.security import verify_api_key
from ..models.common import success_response
from ..models.response import CommonResponse
from ..models.sensor import DoorSensorRequest, MmWaveSensorRequest
from ..services.sensor_service import sensor_service

router = APIRouter(prefix="/sensor", tags=["sensor"], dependencies=[Depends(verify_api_key)])


@router.post("/mmwave", response_model=CommonResponse)
def receive_mmwave(data: MmWaveSensorRequest):
    now = datetime.utcnow().isoformat()
    result = sensor_service.receive_mmwave(data)

    return success_response(
        message="mmWave sensor data received successfully.",
        data={**result, "api_received_at": now},
    )


@router.post("/door", response_model=CommonResponse)
def receive_door(data: DoorSensorRequest):
    now = datetime.utcnow().isoformat()
    result = sensor_service.receive_door(data)

    return success_response(
        message="Door sensor data received successfully.",
        data={**result, "api_received_at": now},
    )
