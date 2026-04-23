from math import hypot
from typing import Optional

from .calibration_service import calibration_service


class ZoneService:
    def resolve_zone(
        self,
        x: Optional[float],
        y: Optional[float],
        explicit_zone: Optional[str] = None,
    ) -> Optional[str]:
        if explicit_zone:
            return explicit_zone

        if x is None or y is None:
            return None

        zones = calibration_service.get_zones()
        best_zone: Optional[str] = None
        best_distance: Optional[float] = None

        for zone_name, zone_data in zones.items():
            if not zone_data or not zone_data.get("calibrated"):
                continue

            center_x = zone_data.get("center_x")
            center_y = zone_data.get("center_y")
            radius = zone_data.get("radius")
            if center_x is None or center_y is None or radius is None:
                continue

            distance = hypot(x - center_x, y - center_y)
            if distance <= radius and (best_distance is None or distance < best_distance):
                best_zone = zone_name
                best_distance = distance

        return best_zone


zone_service = ZoneService()
