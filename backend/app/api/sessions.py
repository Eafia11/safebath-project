from fastapi import APIRouter

from ..models.common import success_response
from ..models.response import CommonResponse
from ..services.session_service import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/active", response_model=CommonResponse)
def get_active_session():
    session = session_service.get_active_session()
    return success_response(
        message="Active session retrieved successfully.",
        data={"session": session.model_dump() if session else None},
    )


@router.post("/start", response_model=CommonResponse)
def start_session():
    session = session_service.start_session()
    return success_response(
        message="Session started successfully.",
        data={"session": session.model_dump()},
    )


@router.post("/end", response_model=CommonResponse)
def end_session():
    session = session_service.end_session()
    return success_response(
        message="Session ended successfully." if session else "No active session to end.",
        data={"session": session.model_dump() if session else None},
    )


@router.get("", response_model=CommonResponse)
def list_sessions():
    sessions = [session.model_dump() for session in session_service.list_sessions()]
    return success_response(
        message="Session list retrieved successfully.",
        data={"sessions": sessions},
    )
