from typing import Dict, List, Optional

from ..models.session import SessionRecord


class SessionRepository:
    def __init__(self):
        self.sessions: Dict[str, SessionRecord] = {}
        self.active_session_id: Optional[str] = None

    def save(self, session: SessionRecord) -> SessionRecord:
        self.sessions[session.session_id] = session.model_copy()
        if session.state == "ACTIVE":
            self.active_session_id = session.session_id
        elif self.active_session_id == session.session_id:
            self.active_session_id = None
        return self.sessions[session.session_id]

    def get(self, session_id: str) -> Optional[SessionRecord]:
        return self.sessions.get(session_id)

    def get_active(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None
        return self.sessions.get(self.active_session_id)

    def list_sessions(self) -> List[SessionRecord]:
        return list(self.sessions.values())

    def clear(self):
        self.sessions.clear()
        self.active_session_id = None


session_repository = SessionRepository()
