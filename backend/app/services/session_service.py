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
            event_count=1,
        )
        self.sessions[session.session_id] = session
        self.active_session_id = session.session_id
        return session

    def ensure_session(self, zone: Optional[str] = None) -> SessionRecord:
        active_session = self.get_active_session()
        if active_session:
            active_session.last_zone = zone or active_session.last_zone
            active_session.event_count += 1
            return active_session

        session = SessionRecord(
            session_id=str(uuid4()),
            started_at=datetime.utcnow().isoformat(),
            start_zone=zone,
            last_zone=zone,
            event_count=1,
        )
        self.sessions[session.session_id] = session
        self.active_session_id = session.session_id
        return session

    def end_session(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None

        session = self.sessions[self.active_session_id]
        ended_at = datetime.utcnow()
        session.ended_at = ended_at.isoformat()
        session.state = "COMPLETED"
        started_at = datetime.fromisoformat(session.started_at)
        session.duration_seconds = round((ended_at - started_at).total_seconds(), 3)
        self.active_session_id = None
        return session

    def record_presence(self, detected: bool, zone: Optional[str] = None) -> Optional[SessionRecord]:
        if detected:
            return self.ensure_session(zone=zone)
        return self.end_session()

    def get_active_session(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None
        return self.sessions[self.active_session_id]

    def list_sessions(self) -> list[SessionRecord]:
        return list(self.sessions.values())


session_service = SessionService()
