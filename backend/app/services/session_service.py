from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from ..models.session import SessionRecord


class SessionService:
    def __init__(self):
        self.sessions: Dict[str, SessionRecord] = {}
        self.active_session_id: Optional[str] = None

    def start_session(self) -> SessionRecord:
        session = SessionRecord(
            session_id=str(uuid4()),
            started_at=datetime.utcnow().isoformat(),
        )
        self.sessions[session.session_id] = session
        self.active_session_id = session.session_id
        return session

    def end_session(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None

        session = self.sessions[self.active_session_id]
        session.ended_at = datetime.utcnow().isoformat()
        session.state = "COMPLETED"
        self.active_session_id = None
        return session

    def get_active_session(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None
        return self.sessions[self.active_session_id]

    def list_sessions(self) -> list[SessionRecord]:
        return list(self.sessions.values())


session_service = SessionService()
