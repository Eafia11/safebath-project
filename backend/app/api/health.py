from fastapi import APIRouter
from app.models.response import CommonResponse
from app.models.common import success_response

router = APIRouter(tags=["health"])

@router.get("/health", response_model=CommonResponse)
def health_check():
    return success_response(
        message="서버가 정상적으로 동작 중입니다.",
        data={"status": "healthy"}
    )