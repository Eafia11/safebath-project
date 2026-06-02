from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.report_service import report_service


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/weekly", response_model=CommonResponse)
def get_weekly_report(days: int = 7):
    return success_response(
        message="Weekly report generated successfully.",
        data=report_service.build_weekly_report(days=days),
    )
