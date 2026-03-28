from datetime import datetime


class CalibrationService:
    def __init__(self):
        self.is_active = False
        self.user_id = None
        self.current_step = None
        self.started_at = None
        self.completed_zones = []
        self.zones = {
            "door": None,
            "toilet": None,
            "sink": None
        }

    def start_calibration(self, user_id: str):
        self.is_active = True
        self.user_id = user_id
        self.current_step = "door"
        self.started_at = datetime.utcnow().isoformat()
        self.completed_zones = []
        self.zones = {
            "door": None,
            "toilet": None,
            "sink": None
        }

        return self.get_status()

    def set_step(self, zone_name: str):
        if not self.is_active:
            return None

        self.current_step = zone_name
        return self.get_status()

    def complete_zone(self, zone_name: str):
        if not self.is_active:
            return None

        if zone_name not in self.completed_zones:
            self.completed_zones.append(zone_name)

        # 지금은 더미 데이터 저장
        self.zones[zone_name] = {
            "center_x": None,
            "center_y": None,
            "radius": None,
            "calibrated": True
        }

        if len(self.completed_zones) == 3:
            self.is_active = False
            self.current_step = None
        else:
            remaining = [z for z in ["door", "toilet", "sink"] if z not in self.completed_zones]
            self.current_step = remaining[0]

        return self.get_status()

    def reset_calibration(self):
        self.is_active = False
        self.user_id = None
        self.current_step = None
        self.started_at = None
        self.completed_zones = []
        self.zones = {
            "door": None,
            "toilet": None,
            "sink": None
        }

        return self.get_status()

    def get_status(self):
        return {
            "is_active": self.is_active,
            "user_id": self.user_id,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "completed_zones": self.completed_zones,
            "progress": f"{len(self.completed_zones)}/3"
        }

    def get_zones(self):
        return self.zones


calibration_service = CalibrationService()