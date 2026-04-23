from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.state_service import state_service

router = APIRouter(tags=["status"])


@router.get("/status", response_model=CommonResponse)
def get_status():
    status = state_service.get_status()
    return success_response(
        message="Current status retrieved successfully.",
        data=status.model_dump(),
    )
