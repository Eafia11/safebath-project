from fastapi import APIRouter, HTTPException

from ..models.calibration import (
    CalibrationCompleteRequest,
    CalibrationStartRequest,
    CalibrationStepRequest,
)
from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.calibration_service import calibration_service

router = APIRouter(prefix="/calibration", tags=["calibration"])


@router.post("/start", response_model=CommonResponse)
def start_calibration(data: CalibrationStartRequest):
    status = calibration_service.start_calibration(user_id=data.user_id)
    return success_response(
        message="Calibration started successfully.",
        data=status,
    )


@router.get("/status", response_model=CommonResponse)
def get_calibration_status():
    return success_response(
        message="Calibration status retrieved successfully.",
        data=calibration_service.get_status(),
    )


@router.post("/step", response_model=CommonResponse)
def set_calibration_step(data: CalibrationStepRequest):
    status = calibration_service.set_step(zone_name=data.zone_name)
    return success_response(
        message="Calibration step updated successfully.",
        data=status,
    )


@router.post("/complete", response_model=CommonResponse)
def complete_calibration_zone(data: CalibrationCompleteRequest):
    try:
        status = calibration_service.complete_zone(
            zone_name=data.zone_name,
            center_x=data.center_x,
            center_y=data.center_y,
            radius=data.radius,
            sample_limit=data.sample_limit,
            min_samples=data.min_samples,
            radius_padding=data.radius_padding,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if status is None:
        raise HTTPException(status_code=400, detail="Calibration is not active.")

    return success_response(
        message=f"{data.zone_name} calibration completed successfully.",
        data=status,
    )


@router.post("/reset", response_model=CommonResponse)
def reset_calibration():
    status = calibration_service.reset_calibration()
    return success_response(
        message="Calibration has been reset.",
        data=status,
    )


@router.get("/zones", response_model=CommonResponse)
def get_calibrated_zones():
    return success_response(
        message="Calibrated zone information retrieved successfully.",
        data=calibration_service.get_zones(),
    )
