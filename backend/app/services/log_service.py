from datetime import datetime


class LogService:
    def __init__(self):
        self.logs = []

    def add_log(self, log_type: str, message: str, data=None, level: str = "info"):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": log_type,
            "level": level,
            "message": message,
            "data": data or {},
        }
        self.logs.append(log_entry)
        return log_entry

    def get_logs(self):
        return self.logs


log_service = LogService()