from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.alert_service import alert_service

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=CommonResponse)
def get_alerts():
    alerts = [alert.model_dump() for alert in alert_service.get_alerts()]
    return success_response(
        message="Alert list retrieved successfully.",
        data={"alerts": alerts},
    )


@router.get("/alerts/latest", response_model=CommonResponse)
def get_latest_alert():
    latest_alert = alert_service.get_latest_alert()
    return success_response(
        message="Latest alert retrieved successfully.",
        data={"alert": latest_alert.model_dump() if latest_alert else None},
    )
