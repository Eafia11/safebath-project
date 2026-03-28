from fastapi import APIRouter
from app.models.common import success_response
from app.models.response import CommonResponse
from app.services.log_service import log_service

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=CommonResponse)
def get_logs():
    return success_response(
        message="로그 목록을 조회했습니다.",
        data={"logs": log_service.get_logs()}
    )