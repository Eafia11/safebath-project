from datetime import datetime, timedelta
from typing import Optional
from app.services.log_service import log_service
from app.services.alert_service import alert_service


class StateService:
    def __init__(self):
        self.current_state = "EMPTY"
        self.last_door_state: Optional[str] = None
        self.last_mmwave_detected: bool = False
        self.last_zone: Optional[str] = None
        self.last_motion_level: Optional[float] = None
        self.last_still_time: Optional[int] = None
        self.last_reason: str = "초기 상태"
        self.last_updated: Optional[str] = None

        self.abnormal_start_time: Optional[datetime] = None
        self.waiting_for_response: bool = False


    def _update_state(self, new_state: str, reason: str):
        previous_state = self.current_state
        self.current_state = new_state
        self.last_reason = reason
        self.last_updated = datetime.utcnow().isoformat()

        log_service.add_log(
            log_type="state",
            message="상태 변경",
            data={
                "previous_state": previous_state,
                "current_state": new_state,
                "reason": reason,
            }
        )

    def process_door_event(self, door_state: str):
        self.last_door_state = door_state

        log_service.add_log(
            log_type="sensor",
            message="도어 센서 데이터 수신",
            data={"door_state": door_state}
        )

        if door_state == "open":
            self._update_state("ENTERING", "문이 열려 사용자의 출입이 감지됨")

        elif door_state == "closed":
            if not self.last_mmwave_detected:
                self._update_state("EMPTY", "문이 닫혔고 사용자 감지가 없음")

        return self.get_status()

    def process_mmwave_event(
        self,
        detected: bool,
        zone: Optional[str] = None,
        motion_level: Optional[float] = None,
        still_time: Optional[int] = None,
    ):
        log_service.add_log(
            log_type="sensor",
            message="mmWave 데이터 수신",
            data={
                "detected": detected,
                "zone": zone,
                "motion_level": motion_level,
                "still_time": still_time,
            }
        )
        
        self.last_mmwave_detected = detected
        self.last_zone = zone
        self.last_motion_level = motion_level
        self.last_still_time = still_time

        # ABNORMAL 이후 응답 대기 중이면 먼저 시간 체크
        if self.waiting_for_response and self.abnormal_start_time:
            now = datetime.utcnow()
            elapsed = now - self.abnormal_start_time

            if elapsed >= timedelta(seconds=10):
                self.waiting_for_response = False
                self._update_state("EMERGENCY", "사용자 응답 없음 → 긴급 상태 전환")

                created_alert = alert_service.create_alert(
                    alert_type="emergency",
                    message="화장실 내 사용자 응답이 없어 긴급 상황으로 판단되었습니다.",
                    level="danger",
                    target="guardian",
                    data={
                        "elapsed_seconds": elapsed.total_seconds(),
                        "current_state": self.current_state,
                        "last_zone": self.last_zone,
                        "last_still_time": self.last_still_time,
                        "reason": self.last_reason,
                    }
                )

                log_service.add_log(
                    log_type="alert",
                    message="응답 없음 → EMERGENCY 전환 및 보호자 알림 생성",
                    data={"alert": created_alert},
                    level="warning"
                )

                return self.get_status()

        if not detected:
            if self.last_door_state == "closed":
                self._update_state("EMPTY", "사용자 감지가 종료됨")
            return self.get_status()

        if still_time is not None and still_time >= 30:
            self._update_state("ABNORMAL", "장시간 움직임 없음")
            self.abnormal_start_time = datetime.utcnow()
            self.waiting_for_response = True
            
            log_service.add_log(
                log_type="alert",
                message="이상행동 감지 → 스피커 경고 발생",
                data={"action": "speaker_triggered"},
                level="warning"
            )

            return self.get_status()
            
        if zone == "toilet":
            self._update_state("TOILET_USE", "변기 존에서 사용자 체류 감지")
            return self.get_status()

        if motion_level is not None and motion_level > 0:
            self._update_state("ACTIVE", "내부에서 일반 활동 감지")
            return self.get_status()

        self._update_state("ACTIVE", "사용자 감지됨")
        return self.get_status()

    def process_button_event(self, button_type: str):
        log_service.add_log(
            log_type="device",
            message="버튼 입력 수신",
            data={"button_type": button_type}
        )

        if button_type == "confirm_safe":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self._update_state("ACTIVE", "사용자가 안전 확인 버튼을 누름")

        elif button_type == "emergency_call":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self._update_state("EMERGENCY", "사용자가 긴급 호출 버튼을 누름")

            created_alert = alert_service.create_alert(
                alert_type="emergency",
                message="사용자가 긴급 호출 버튼을 눌렀습니다.",
                level="danger",
                target="guardian",
                data={
                    "current_state": self.current_state,
                    "reason": self.last_reason,
                }
            )

            log_service.add_log(
            log_type="alert",
            message="긴급 호출 버튼 입력 → 보호자 알림 생성",
            data={"alert": created_alert},
            level="warning"
            )

        elif button_type == "reset":
            self.waiting_for_response = False
            self.abnormal_start_time = None
            self._update_state("EMPTY", "사용자가 상태를 초기화함")

        return self.get_status()

    def get_status(self):
        return {
            "current_state": self.current_state,
            "last_door_state": self.last_door_state,
            "last_mmwave_detected": self.last_mmwave_detected,
            "last_zone": self.last_zone,
            "last_motion_level": self.last_motion_level,
            "last_still_time": self.last_still_time,
            "last_reason": self.last_reason,
            "last_updated": self.last_updated,
            "waiting_for_response": self.waiting_for_response,
            "abnormal_start_time": self.abnormal_start_time.isoformat() if self.abnormal_start_time else None,
        }


state_service = StateService()