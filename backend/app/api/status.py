from fastapi import APIRouter
from app.models.common import success_response
from app.models.response import CommonResponse
from app.services.state_service import state_service

router = APIRouter(tags=["status"])


@router.get("/status", response_model=CommonResponse)
def get_status():
    return success_response(
        message="현재 시스템 상태를 조회했습니다.",
        data=state_service.get_status()
    )