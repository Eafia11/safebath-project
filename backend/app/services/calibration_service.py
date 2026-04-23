from datetime import datetime


class CalibrationService:
    def __init__(self):
        self.is_active = False
        self.user_id = None
        self.current_step = None
        self.started_at = None
        self.completed_zones = []
        self.default_zones = {
            "door": {"center_x": 0.0, "center_y": 0.0, "radius": 0.8},
            "toilet": {"center_x": 1.25, "center_y": 0.78, "radius": 0.7},
            "sink": {"center_x": 2.1, "center_y": 0.95, "radius": 0.7},
        }
        self.zones = {
            "door": None,
            "toilet": None,
            "sink": None,
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
            "sink": None,
        }
        return self.get_status()

    def set_step(self, zone_name: str):
        if not self.is_active:
            return None

        self.current_step = zone_name
        return self.get_status()

    def complete_zone(
        self,
        zone_name: str,
        center_x: float | None = None,
        center_y: float | None = None,
        radius: float | None = None,
    ):
        if not self.is_active:
            return None

        if zone_name not in self.completed_zones:
            self.completed_zones.append(zone_name)

        default_zone = self.default_zones.get(zone_name, {})
        self.zones[zone_name] = {
            "center_x": center_x if center_x is not None else default_zone.get("center_x"),
            "center_y": center_y if center_y is not None else default_zone.get("center_y"),
            "radius": radius if radius is not None else default_zone.get("radius"),
            "calibrated": True,
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
            "sink": None,
        }
        return self.get_status()

    def get_status(self):
        return {
            "is_active": self.is_active,
            "user_id": self.user_id,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "completed_zones": self.completed_zones,
            "progress": f"{len(self.completed_zones)}/3",
        }

    def get_zones(self):
        return self.zones


calibration_service = CalibrationService()
