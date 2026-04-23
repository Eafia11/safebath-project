from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class RuleBasedService:
    def evaluate_response_timeout(
        self,
        waiting_for_response: bool,
        abnormal_start_time: Optional[datetime],
        timeout_seconds: int = 10,
    ) -> Dict[str, Any]:
        if not waiting_for_response or not abnormal_start_time:
            return {
                "triggered": False,
                "rule_type": None,
                "reason": None,
                "elapsed_seconds": 0.0,
            }

        elapsed = datetime.utcnow() - abnormal_start_time
        triggered = elapsed >= timedelta(seconds=timeout_seconds)
        return {
            "triggered": triggered,
            "rule_type": "response_timeout" if triggered else None,
            "reason": "No user response after abnormal activity" if triggered else None,
            "elapsed_seconds": round(elapsed.total_seconds(), 3),
        }

    def evaluate_mmwave_rules(
        self,
        detected: bool,
        zone: Optional[str] = None,
        motion_level: Optional[float] = None,
        still_time: Optional[int] = None,
        last_door_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not detected:
            if last_door_state == "closed":
                return {
                    "rule_type": "occupancy_ended",
                    "next_state": "EMPTY",
                    "reason": "Occupancy detection ended",
                    "triggered": True,
                }
            return {
                "rule_type": "no_presence",
                "next_state": None,
                "reason": None,
                "triggered": False,
            }

        if still_time is not None and still_time >= 30:
            return {
                "rule_type": "prolonged_inactivity",
                "next_state": "ABNORMAL",
                "reason": "No movement detected for a prolonged period",
                "triggered": True,
            }

        if zone == "toilet":
            return {
                "rule_type": "toilet_zone_detected",
                "next_state": "TOILET_USE",
                "reason": "User detected in toilet zone",
                "triggered": True,
            }

        if motion_level is not None and motion_level > 0:
            return {
                "rule_type": "motion_detected",
                "next_state": "ACTIVE",
                "reason": "General movement detected",
                "triggered": True,
            }

        return {
            "rule_type": "presence_detected",
            "next_state": "ACTIVE",
            "reason": "Occupancy detected",
            "triggered": True,
        }


rule_based_service = RuleBasedService()
