from datetime import datetime, timedelta
from typing import Optional

from ..detectors.inactivity_detector import inactivity_detector
from ..models.status import StatusSnapshot
from .alert_service import alert_service
from .log_service import log_service


class StateService:
    RESPONSE_TIMEOUT_SECONDS = 20

    def __init__(self):
        self.current_state = "EMPTY"
        self.last_door_state: Optional[str] = None
        self.last_mmwave_detected = False
        self.last_mmwave_seen_at: Optional[datetime] = None
        self.last_zone: Optional[str] = None
        self.last_motion_level: Optional[float] = None
        self.last_still_time: Optional[int] = None
        self.last_reason = "Initial state"
        self.last_emergency_source: Optional[str] = None
        self.last_updated: Optional[str] = None
        self.abnormal_start_time: Optional[datetime] = None
        self.waiting_for_response = False
        self.pending_response_type: Optional[str] = None
        self.last_fall_detected = False
        self.last_fall_score = 0.0
        self.last_fall_at: Optional[str] = None
        self.pending_fall_reason: Optional[str] = None

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
        elif door_state == "closed":
            if self.last_mmwave_detected and self._is_mmwave_online():
                self._update_state("ACTIVE", "Door closed and occupant was detected")
            else:
                self.last_mmwave_detected = False
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
        self.last_mmwave_seen_at = datetime.utcnow()
        self.last_zone = zone
        self.last_motion_level = motion_level
        self.last_still_time = still_time

        if self._apply_response_timeout():
            return self.get_status()

        mmwave_rule = inactivity_detector.evaluate_mmwave_rules(
            detected=detected,
            zone=zone,
            motion_level=motion_level,
            still_time=still_time,
            last_door_state=self.last_door_state,
        )
        if not mmwave_rule["triggered"]:
            if self.current_state != "EMERGENCY":
                self.last_emergency_source = None
            return self.get_status()

        self._update_state(mmwave_rule["next_state"], mmwave_rule["reason"])
        if mmwave_rule["rule_type"] == "prolonged_inactivity":
            self.abnormal_start_time = datetime.utcnow()
            self.waiting_for_response = True
            self.pending_response_type = "inactivity"
            log_service.add_log(
                log_type="alert",
                message="Abnormal inactivity detected and speaker warning triggered",
                data={"action": "speaker_triggered"},
                level="warning",
            )
        return self.get_status()

    def mark_possible_fall_detected(self, score: float, reason: str) -> StatusSnapshot:
        self.last_fall_detected = False
        self.last_fall_score = score
        self.last_fall_at = None
        self.pending_fall_reason = reason
        self.waiting_for_response = True
        self.pending_response_type = "fall"
        self.abnormal_start_time = datetime.utcnow()
        self._update_state("ABNORMAL", "Possible fall detected; waiting for user response")
        log_service.add_log(
            log_type="alert",
            message="Possible fall detected and speaker warning triggered",
            data={
                "fall_score": score,
                "reason": reason,
                "action": "speaker_triggered",
            },
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
            self.pending_response_type = None
            self.pending_fall_reason = None
            self.last_fall_detected = False
            self.last_emergency_source = None
            if self.last_mmwave_detected:
                self._update_state("ACTIVE", "User confirmed safety")
            else:
                self._update_state("EMPTY", "User confirmed safety and no occupant was detected")
        elif button_type == "emergency_call":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self.pending_response_type = None
            self.pending_fall_reason = None
            self.last_emergency_source = "manual"
            self._update_state("EMERGENCY", "User triggered emergency call")
            created_alert = alert_service.create_alert(
                alert_type="emergency",
                message="Emergency call button was pressed by the user.",
                level="danger",
                target="guardian",
                data={
                    "emergency_source": "manual",
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
            self.pending_response_type = None
            self.pending_fall_reason = None
            self.last_fall_detected = False
            self.last_fall_score = 0.0
            self.last_fall_at = None
            self.last_emergency_source = None
            self._update_state("EMPTY", "State reset requested by user")

        return self.get_status()

    def get_status(self) -> StatusSnapshot:
        self._apply_response_timeout()
        self._apply_mmwave_stale_timeout()
        mmwave_online = self._is_mmwave_online()
        return StatusSnapshot(
            current_state=self.current_state,
            last_door_state=self.last_door_state,
            last_mmwave_detected=self.last_mmwave_detected,
            last_mmwave_seen_at=self.last_mmwave_seen_at.isoformat()
            if self.last_mmwave_seen_at
            else None,
            mmwave_online=mmwave_online,
            last_zone=self.last_zone,
            last_motion_level=self.last_motion_level,
            last_still_time=self.last_still_time,
            last_reason=self.last_reason,
            last_emergency_source=self.last_emergency_source,
            last_updated=self.last_updated,
            waiting_for_response=self.waiting_for_response,
            pending_response_type=self.pending_response_type,
            abnormal_start_time=self.abnormal_start_time.isoformat()
            if self.abnormal_start_time
            else None,
            last_fall_detected=self.last_fall_detected,
            last_fall_score=self.last_fall_score,
            last_fall_at=self.last_fall_at,
        )

    def _is_mmwave_online(self, timeout_seconds: int = 10) -> bool:
        if self.last_mmwave_seen_at is None:
            return False
        return datetime.utcnow() - self.last_mmwave_seen_at < timedelta(seconds=timeout_seconds)

    def _apply_response_timeout(self) -> bool:
        timeout_rule = inactivity_detector.evaluate_response_timeout(
            waiting_for_response=self.waiting_for_response,
            abnormal_start_time=self.abnormal_start_time,
            timeout_seconds=self.RESPONSE_TIMEOUT_SECONDS,
        )
        if not timeout_rule["triggered"]:
            return False

        self.waiting_for_response = False
        response_type = self.pending_response_type or "inactivity"
        self.pending_response_type = None
        self.last_emergency_source = response_type
        if response_type == "fall":
            self.last_fall_detected = True
            self.last_fall_at = datetime.utcnow().isoformat()

        alert_message = (
            "No user response after possible fall; emergency alert created."
            if response_type == "fall"
            else "No user response after abnormal activity; emergency alert created."
        )
        reason = (
            "No user response after possible fall"
            if response_type == "fall"
            else timeout_rule["reason"]
        )
        self._update_state("EMERGENCY", reason)
        created_alert = alert_service.create_alert(
            alert_type="emergency",
            message=alert_message,
            level="danger",
            target="guardian",
            data={
                "emergency_source": response_type,
                "elapsed_seconds": timeout_rule["elapsed_seconds"],
                "current_state": self.current_state,
                "last_zone": self.last_zone,
                "last_still_time": self.last_still_time,
                "fall_score": self.last_fall_score if response_type == "fall" else None,
                "reason": self.last_reason,
            },
        )
        log_service.add_log(
            log_type="alert",
            message="Fall alert created after no response"
            if response_type == "fall"
            else "Emergency alert created after no response",
            data={"alert": created_alert.model_dump()},
            level="warning",
        )
        return True

    def _apply_mmwave_stale_timeout(self, timeout_seconds: int = 10) -> None:
        if self.current_state not in {"ACTIVE", "TOILET_USE"}:
            return
        if self.last_mmwave_seen_at is None:
            self.last_mmwave_detected = False
            self._update_state("EMPTY", "No mmWave data has been received")
            return
        if datetime.utcnow() - self.last_mmwave_seen_at < timedelta(seconds=timeout_seconds):
            return

        self.last_mmwave_detected = False
        self.last_zone = None
        self.last_motion_level = 0.0
        self.last_still_time = 0
        self._update_state("EMPTY", "mmWave data timed out")


state_service = StateService()
