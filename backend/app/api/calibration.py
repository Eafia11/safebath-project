from fastapi import APIRouter

from ..models.calibration import (
    CalibrationStartRequest,
    CalibrationStepRequest,
    CalibrationCompleteRequest,
)
from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.calibration_service import calibration_service

router = APIRouter(prefix="/calibration", tags=["calibration"])


@router.post("/start", response_model=CommonResponse)
def start_calibration(data: CalibrationStartRequest):
    status = calibration_service.start_calibration(user_id=data.user_id)
    return success_response(
        message="존 캘리브레이션을 시작했습니다.",
        data=status
    )


@router.get("/status", response_model=CommonResponse)
def get_calibration_status():
    return success_response(
        message="캘리브레이션 상태를 조회했습니다.",
        data=calibration_service.get_status()
    )


@router.post("/step", response_model=CommonResponse)
def set_calibration_step(data: CalibrationStepRequest):
    status = calibration_service.set_step(zone_name=data.zone_name)
    return success_response(
        message="캘리브레이션 단계를 변경했습니다.",
        data=status
    )


@router.post("/complete", response_model=CommonResponse)
def complete_calibration_zone(data: CalibrationCompleteRequest):
    status = calibration_service.complete_zone(zone_name=data.zone_name)
    return success_response(
        message=f"{data.zone_name} 존 캘리브레이션을 완료했습니다.",
        data=status
    )


@router.post("/reset", response_model=CommonResponse)
def reset_calibration():
    status = calibration_service.reset_calibration()
    return success_response(
        message="캘리브레이션을 초기화했습니다.",
        data=status
    )


@router.get("/zones", response_model=CommonResponse)
def get_calibrated_zones():
    return success_response(
        message="저장된 존 정보를 조회했습니다.",
        data=calibration_service.get_zones()
    )
