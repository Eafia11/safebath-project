from fastapi import APIRouter
from datetime import datetime
from app.models.common import success_response
from app.models.response import CommonResponse
from app.models.device import ButtonRequest, SpeakerRequest
from app.services.log_service import log_service
from app.services.state_service import state_service

router = APIRouter(prefix="/device", tags=["device"])


@router.post("/button", response_model=CommonResponse)
def receive_button(data: ButtonRequest):
    now = datetime.utcnow().isoformat()

    status = state_service.process_button_event(
        button_type=data.button_type
    )

    return success_response(
        message="버튼 입력 처리 완료",
        data={
            "timestamp": now,
            "received": True,
            "device": "button",
            "payload": data.model_dump(),
            "status": status,
        }
    )


@router.post("/speaker", response_model=CommonResponse)
def trigger_speaker(data: SpeakerRequest):
    now = datetime.utcnow().isoformat()

    return success_response(
        message="스피커 출력 요청 처리 완료",
        data={
            "timestamp": now,
            "requested": True,
            "device": "speaker",
            "payload": data.model_dump(),
        }
    )