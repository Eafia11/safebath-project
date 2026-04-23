from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.alert_service import alert_service
from ..services.device_service import device_service
from ..services.log_service import log_service
from ..services.session_service import session_service
from ..services.state_service import state_service

router = APIRouter(prefix="/admin", tags=["admin"])


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
