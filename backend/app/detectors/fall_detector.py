from datetime import datetime
from typing import Any, Dict, Optional

from ..utils.math_utils import distance_3d

class FallDetector:
    def __init__(self):
        self.last_sample: Optional[Dict[str, Any]] = None

    def evaluate(
        self,
        *,
        detected: bool,
        x: Optional[float],
        y: Optional[float],
        z: Optional[float],
        still_time: Optional[int],
        velocity: Optional[float] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        height_drop = 0.0
        speed_change = 0.0

        if self.last_sample:
            previous_z = self.last_sample.get("z")
            if z is not None and previous_z is not None:
                height_drop = max(previous_z - z, 0.0)

            previous_velocity = self.last_sample.get("velocity")
            if velocity is None:
                velocity = self._estimate_velocity(now, x, y, z)
            if velocity is not None and previous_velocity is not None:
                speed_change = abs(velocity - previous_velocity)
        elif velocity is None:
            velocity = 0.0

        motion_stopped = (still_time or 0) >= 10
        height_rule = height_drop >= 0.35
        speed_rule = speed_change >= 0.8
        detected_fall = bool(detected and height_rule and speed_rule and motion_stopped)

        score = round(
            min(
                (height_drop / 0.35 if height_drop else 0.0)
                + (speed_change / 0.8 if speed_change else 0.0)
                + min((still_time or 0) / 10.0, 1.0),
                3.0,
            )
            / 3.0,
            4,
        )

        result = {
            "detected": detected_fall,
            "score": score,
            "height_drop": round(height_drop, 4),
            "speed_change": round(speed_change, 4),
            "still_time": still_time or 0,
            "used_velocity": round(velocity or 0.0, 4),
            "reason": (
                "Height drop, speed change, and inactivity thresholds were all met."
                if detected_fall
                else "Fall thresholds were not all met."
            ),
        }

        self.last_sample = {
            "timestamp": now,
            "x": x,
            "y": y,
            "z": z,
            "velocity": velocity or 0.0,
        }
        return result

    def _estimate_velocity(
        self,
        now: datetime,
        x: Optional[float],
        y: Optional[float],
        z: Optional[float],
    ) -> Optional[float]:
        if not self.last_sample:
            return None

        previous_timestamp = self.last_sample.get("timestamp")
        previous_x = self.last_sample.get("x")
        previous_y = self.last_sample.get("y")
        previous_z = self.last_sample.get("z")
        if (
            previous_timestamp is None
            or x is None
            or y is None
            or z is None
            or previous_x is None
            or previous_y is None
            or previous_z is None
        ):
            return None

        elapsed = max((now - previous_timestamp).total_seconds(), 0.001)
        distance = distance_3d(x, y, z, previous_x, previous_y, previous_z)
        if distance is None:
            return None
        return distance / elapsed


fall_detector = FallDetector()
