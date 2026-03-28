from datetime import datetime


class AlertService:
    def __init__(self):
        self.alerts = []

    def create_alert(self, alert_type: str, message: str, level: str = "warning", target: str = "guardian", data=None):
        alert = {
            "id": len(self.alerts) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "type": alert_type,
            "level": level,
            "target": target,
            "message": message,
            "data": data or {},
            "status": "created"
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self):
        return self.alerts

    def get_latest_alert(self):
        if not self.alerts:
            return None
        return self.alerts[-1]


alert_service = AlertService()