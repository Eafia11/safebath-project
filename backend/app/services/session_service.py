from typing import Dict, Optional
from uuid import uuid4

from ..models.session import SessionRecord
from ..repositories.session_repository import session_repository
from ..utils.time_utils import parse_iso_datetime, seconds_between, utc_now, utc_now_iso


class SessionService:
    def __init__(self):
        self.sessions: Dict[str, SessionRecord] = {}
        self.active_session_id: Optional[str] = None

    def start_session(self) -> SessionRecord:
        session = SessionRecord(
            session_id=str(uuid4()),
            started_at=utc_now_iso(),
            event_count=1,
        )
        self.sessions[session.session_id] = session
        self.active_session_id = session.session_id
        session_repository.save(session)
        return session

    def ensure_session(self, zone: Optional[str] = None) -> SessionRecord:
        active_session = self.get_active_session()
        if active_session:
            active_session.last_zone = zone or active_session.last_zone
            active_session.event_count += 1
            session_repository.save(active_session)
            return active_session

        session = SessionRecord(
            session_id=str(uuid4()),
            started_at=utc_now_iso(),
            start_zone=zone,
            last_zone=zone,
            event_count=1,
        )
        self.sessions[session.session_id] = session
        self.active_session_id = session.session_id
        session_repository.save(session)
        return session

    def end_session(self) -> Optional[SessionRecord]:
        if not self.active_session_id:
            return None

        session = self.sessions[self.active_session_id]
        ended_at = utc_now()
        session.ended_at = ended_at.isoformat()
        session.state = "COMPLETED"
        started_at = parse_iso_datetime(session.started_at)
        if started_at:
            session.duration_seconds = seconds_between(started_at, ended_at)
        self.active_session_id = None
        session_repository.save(session)
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
