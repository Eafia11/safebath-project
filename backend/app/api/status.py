from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.session_service import session_service
from ..services.state_service import state_service

router = APIRouter(tags=["status"])


@router.get("/status", response_model=CommonResponse)
def get_status():
    status = state_service.get_status()
    active_session = session_service.get_active_session()
    return success_response(
        message="Current status retrieved successfully.",
        data={
            **status.model_dump(),
            "active_session": active_session.model_dump() if active_session else None,
        },
    )
