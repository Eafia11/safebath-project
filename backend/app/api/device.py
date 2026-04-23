from datetime import datetime

from fastapi import APIRouter

from ..models.common import success_response
from ..models.device import ButtonRequest, HeartbeatRequest, SpeakerRequest
from ..models.response import CommonResponse
from ..services.device_service import device_service

router = APIRouter(prefix="/device", tags=["device"])


@router.post("/button", response_model=CommonResponse)
def receive_button(data: ButtonRequest):
    now = datetime.utcnow().isoformat()
    result = device_service.process_button(data)
    return success_response(
        message="Button input processed successfully.",
        data={**result, "api_received_at": now},
    )


@router.post("/speaker", response_model=CommonResponse)
def trigger_speaker(data: SpeakerRequest):
    now = datetime.utcnow().isoformat()
    result = device_service.trigger_speaker(data)
    return success_response(
        message="Speaker request processed successfully.",
        data={**result, "api_received_at": now},
    )


@router.post("/heartbeat", response_model=CommonResponse)
def receive_heartbeat(data: HeartbeatRequest):
    now = datetime.utcnow().isoformat()
    result = device_service.receive_heartbeat(data)
    return success_response(
        message="Device heartbeat received successfully.",
        data={**result, "api_received_at": now},
    )


@router.get("/status", response_model=CommonResponse)
def get_device_status():
    return success_response(
        message="Device status retrieved successfully.",
        data={"devices": device_service.get_devices()},
    )
