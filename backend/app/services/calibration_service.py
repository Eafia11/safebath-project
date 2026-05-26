from datetime import datetime
from statistics import fmean

from ..repositories.sensor_repository import sensor_repository
from ..utils.math_utils import distance_2d


ZONE_ORDER = ["toilet", "sink", "bath"]


class CalibrationService:
    def __init__(self):
        self.is_active = False
        self.user_id = None
        self.current_step = None
        self.started_at = None
        self.completed_zones = []
        self.default_zones = {
            "toilet": {"center_x": 1.25, "center_y": 0.78, "radius": 0.7},
            "sink": {"center_x": 2.1, "center_y": 0.95, "radius": 0.7},
            "bath": {"center_x": 1.7, "center_y": 1.2, "radius": 0.7},
        }
        self.zones = {zone_name: None for zone_name in ZONE_ORDER}

    def start_calibration(self, user_id: str):
        self.is_active = True
        self.user_id = user_id
        self.current_step = ZONE_ORDER[0]
        self.started_at = datetime.utcnow().isoformat()
        self.completed_zones = []
        self.zones = {zone_name: None for zone_name in ZONE_ORDER}
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
        sample_limit: int = 20,
        min_samples: int = 5,
        radius_padding: float = 0.05,
    ):
        if not self.is_active:
            return None

        calibration_source = "manual"
        sample_count = 0
        if center_x is None or center_y is None or radius is None:
            sampled_zone = self._calibrate_from_recent_samples(
                center_x=center_x,
                center_y=center_y,
                radius=radius,
                sample_limit=sample_limit,
                min_samples=min_samples,
                radius_padding=radius_padding,
            )
            center_x = sampled_zone["center_x"]
            center_y = sampled_zone["center_y"]
            radius = sampled_zone["radius"]
            calibration_source = sampled_zone["source"]
            sample_count = sampled_zone["sample_count"]

        if zone_name not in self.completed_zones:
            self.completed_zones.append(zone_name)

        self.zones[zone_name] = {
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius,
            "calibrated": True,
            "source": calibration_source,
            "sample_count": sample_count,
        }

        if len(self.completed_zones) == len(ZONE_ORDER):
            self.is_active = False
            self.current_step = None
        else:
            remaining = [z for z in ZONE_ORDER if z not in self.completed_zones]
            self.current_step = remaining[0]

        return self.get_status()

    def _calibrate_from_recent_samples(
        self,
        *,
        center_x: float | None,
        center_y: float | None,
        radius: float | None,
        sample_limit: int,
        min_samples: int,
        radius_padding: float,
    ):
        points = sensor_repository.recent_mmwave_points(limit=sample_limit)
        if len(points) < min_samples:
            raise ValueError(
                f"At least {min_samples} detected mmWave samples are required; "
                f"only {len(points)} are available."
            )

        computed_x = fmean(point["x"] for point in points)
        computed_y = fmean(point["y"] for point in points)
        resolved_x = center_x if center_x is not None else computed_x
        resolved_y = center_y if center_y is not None else computed_y

        if radius is None:
            spread = max(distance_2d(point["x"], point["y"], resolved_x, resolved_y) for point in points)
            radius = max(0.1, round(spread + radius_padding, 3))

        return {
            "center_x": round(resolved_x, 4),
            "center_y": round(resolved_y, 4),
            "radius": round(radius, 4),
            "source": "recent_samples",
            "sample_count": len(points),
        }

    def reset_calibration(self):
        self.is_active = False
        self.user_id = None
        self.current_step = None
        self.started_at = None
        self.completed_zones = []
        self.zones = {zone_name: None for zone_name in ZONE_ORDER}
        return self.get_status()

    def get_status(self):
        return {
            "is_active": self.is_active,
            "user_id": self.user_id,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "completed_zones": self.completed_zones,
            "progress": f"{len(self.completed_zones)}/{len(ZONE_ORDER)}",
            "zones": self.zones,
        }

    def get_zones(self):
        return self.zones


calibration_service = CalibrationService()
