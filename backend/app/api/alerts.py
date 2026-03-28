from fastapi import APIRouter
from app.models.common import success_response
from app.models.response import CommonResponse
from app.services.alert_service import alert_service

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=CommonResponse)
def get_alerts():
    return success_response(
        message="알림 목록을 조회했습니다.",
        data={"alerts": alert_service.get_alerts()}
    )


@router.get("/alerts/latest", response_model=CommonResponse)
def get_latest_alert():
    return success_response(
        message="최신 알림을 조회했습니다.",
        data={"alert": alert_service.get_latest_alert()}
    )