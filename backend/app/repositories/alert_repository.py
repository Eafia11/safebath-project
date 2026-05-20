from typing import List, Optional

from ..models.alert import AlertEvent


class AlertRepository:
    def __init__(self):
        self.alerts: List[AlertEvent] = []

    def save(self, alert: AlertEvent) -> AlertEvent:
        stored_alert = alert.model_copy()
        self.alerts.append(stored_alert)
        return stored_alert

    def list_alerts(self) -> List[AlertEvent]:
        return self.alerts

    def get_latest(self) -> Optional[AlertEvent]:
        if not self.alerts:
            return None
        return self.alerts[-1]

    def clear(self):
        self.alerts.clear()


alert_repository = AlertRepository()
