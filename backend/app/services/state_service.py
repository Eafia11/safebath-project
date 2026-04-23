from datetime import datetime
from typing import Optional

from ..models.status import StatusSnapshot
from .alert_service import alert_service
from .log_service import log_service
from .rule_based_service import rule_based_service


class StateService:
    def __init__(self):
        self.current_state = "EMPTY"
        self.last_door_state: Optional[str] = None
        self.last_mmwave_detected = False
        self.last_zone: Optional[str] = None
        self.last_motion_level: Optional[float] = None
        self.last_still_time: Optional[int] = None
        self.last_reason = "Initial state"
        self.last_updated: Optional[str] = None
        self.abnormal_start_time: Optional[datetime] = None
        self.waiting_for_response = False
        self.last_fall_detected = False
        self.last_fall_score = 0.0
        self.last_fall_at: Optional[str] = None

    def _update_state(self, new_state: str, reason: str):
        previous_state = self.current_state
        self.current_state = new_state
        self.last_reason = reason
        self.last_updated = datetime.utcnow().isoformat()
        log_service.add_log(
            log_type="state",
            message="State changed",
            data={
                "previous_state": previous_state,
                "current_state": new_state,
                "reason": reason,
            },
        )

    def process_door_event(self, door_state: str) -> StatusSnapshot:
        self.last_door_state = door_state
        log_service.add_log(
            log_type="sensor",
            message="Door sensor event received",
            data={"door_state": door_state},
        )

        if door_state == "open":
            self._update_state("ENTERING", "Door opened and entry was detected")
        elif door_state == "closed" and not self.last_mmwave_detected:
            self._update_state("EMPTY", "Door closed and no occupant was detected")

        return self.get_status()

    def process_mmwave_event(
        self,
        detected: bool,
        zone: Optional[str] = None,
        motion_level: Optional[float] = None,
        still_time: Optional[int] = None,
    ) -> StatusSnapshot:
        log_service.add_log(
            log_type="sensor",
            message="mmWave sensor event received",
            data={
                "detected": detected,
                "zone": zone,
                "motion_level": motion_level,
                "still_time": still_time,
            },
        )

        self.last_mmwave_detected = detected
        self.last_zone = zone
        self.last_motion_level = motion_level
        self.last_still_time = still_time

        timeout_rule = rule_based_service.evaluate_response_timeout(
            waiting_for_response=self.waiting_for_response,
            abnormal_start_time=self.abnormal_start_time,
            timeout_seconds=10,
        )
        if timeout_rule["triggered"]:
            self.waiting_for_response = False
            self._update_state("EMERGENCY", timeout_rule["reason"])
            created_alert = alert_service.create_alert(
                alert_type="emergency",
                message="No user response after abnormal activity; emergency alert created.",
                level="danger",
                target="guardian",
                data={
                    "elapsed_seconds": timeout_rule["elapsed_seconds"],
                    "current_state": self.current_state,
                    "last_zone": self.last_zone,
                    "last_still_time": self.last_still_time,
                    "reason": self.last_reason,
                },
            )
            log_service.add_log(
                log_type="alert",
                message="Emergency alert created after no response",
                data={"alert": created_alert.model_dump()},
                level="warning",
            )
            return self.get_status()

        mmwave_rule = rule_based_service.evaluate_mmwave_rules(
            detected=detected,
            zone=zone,
            motion_level=motion_level,
            still_time=still_time,
            last_door_state=self.last_door_state,
        )
        if not mmwave_rule["triggered"]:
            return self.get_status()

        self._update_state(mmwave_rule["next_state"], mmwave_rule["reason"])
        if mmwave_rule["rule_type"] == "prolonged_inactivity":
            self.abnormal_start_time = datetime.utcnow()
            self.waiting_for_response = True
            log_service.add_log(
                log_type="alert",
                message="Abnormal inactivity detected and speaker warning triggered",
                data={"action": "speaker_triggered"},
                level="warning",
            )
        return self.get_status()

    def mark_fall_detected(self, score: float, reason: str) -> StatusSnapshot:
        self.last_fall_detected = True
        self.last_fall_score = score
        self.last_fall_at = datetime.utcnow().isoformat()
        self.waiting_for_response = False
        self.abnormal_start_time = None
        self._update_state("EMERGENCY", reason)

        created_alert = alert_service.create_alert(
            alert_type="fall",
            message="Possible fall detected from mmWave sensor data.",
            level="danger",
            target="guardian",
            data={
                "fall_score": score,
                "current_state": self.current_state,
                "last_zone": self.last_zone,
                "reason": reason,
            },
        )
        log_service.add_log(
            log_type="alert",
            message="Fall alert created from mmWave rule evaluation",
            data={"alert": created_alert.model_dump()},
            level="warning",
        )
        return self.get_status()

    def process_button_event(self, button_type: str) -> StatusSnapshot:
        log_service.add_log(
            log_type="device",
            message="Button input received",
            data={"button_type": button_type},
        )

        if button_type == "confirm_safe":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self.last_fall_detected = False
            self._update_state("ACTIVE", "User confirmed safety")
        elif button_type == "emergency_call":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self._update_state("EMERGENCY", "User triggered emergency call")
            created_alert = alert_service.create_alert(
                alert_type="emergency",
                message="Emergency call button was pressed by the user.",
                level="danger",
                target="guardian",
                data={
                    "current_state": self.current_state,
                    "reason": self.last_reason,
                },
            )
            log_service.add_log(
                log_type="alert",
                message="Emergency alert created from button input",
                data={"alert": created_alert.model_dump()},
                level="warning",
            )
        elif button_type == "reset":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self.last_fall_detected = False
            self.last_fall_score = 0.0
            self.last_fall_at = None
            self._update_state("EMPTY", "State reset requested by user")

        return self.get_status()

    def get_status(self) -> StatusSnapshot:
        return StatusSnapshot(
            current_state=self.current_state,
            last_door_state=self.last_door_state,
            last_mmwave_detected=self.last_mmwave_detected,
            last_zone=self.last_zone,
            last_motion_level=self.last_motion_level,
            last_still_time=self.last_still_time,
            last_reason=self.last_reason,
            last_updated=self.last_updated,
            waiting_for_response=self.waiting_for_response,
            abnormal_start_time=self.abnormal_start_time.isoformat()
            if self.abnormal_start_time
            else None,
            last_fall_detected=self.last_fall_detected,
            last_fall_score=self.last_fall_score,
            last_fall_at=self.last_fall_at,
        )


state_service = StateService()
