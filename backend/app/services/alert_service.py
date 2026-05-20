from datetime import datetime

from ..models.alert import AlertEvent
from ..repositories.alert_repository import alert_repository


class AlertService:
    def __init__(self):
        self.alerts: list[AlertEvent] = []

    def create_alert(
        self,
        alert_type: str,
        message: str,
        level: str = "warning",
        target: str = "guardian",
        data=None,
    ) -> AlertEvent:
        alert = AlertEvent(
            id=len(self.alerts) + 1,
            timestamp=datetime.utcnow().isoformat(),
            type=alert_type,
            level=level,
            target=target,
            message=message,
            data=data or {},
            status="created",
        )
        self.alerts.append(alert)
        alert_repository.save(alert)
        return alert

    def get_alerts(self) -> list[AlertEvent]:
        return self.alerts

    def get_latest_alert(self) -> AlertEvent | None:
        if not self.alerts:
            return None
        return self.alerts[-1]


alert_service = AlertService()
