from typing import Any, Dict

from ..detectors.fall_detector import fall_detector
from ..detectors.fusion_detector import fusion_detector
from ..models.device import SpeakerRequest
from ..models.sensor import DoorSensorRequest, MmWaveSensorRequest
from ..repositories.feature_repository import feature_repository
from ..repositories.sensor_repository import sensor_repository
from ..repositories.status_repository import status_repository
from ..utils.time_utils import utc_now_iso
from ..utils.validators import validate_mmwave_coordinates
from .anomaly_service import anomaly_service
from .device_service import device_service
from .feature_service import feature_service
from .log_service import log_service
from .session_service import session_service
from .state_service import state_service
from .zone_service import zone_service


class SensorService:
    def __init__(self):
        self.last_events: Dict[str, Dict[str, Any]] = {}

    def _remember_event(self, sensor_name: str, payload: Dict[str, Any]):
        self.last_events[sensor_name] = {
            "timestamp": utc_now_iso(),
            "payload": payload,
        }

    def receive_mmwave(self, data: MmWaveSensorRequest) -> Dict[str, Any]:
        if not validate_mmwave_coordinates(data.x, data.y, data.z):
            raise ValueError("Invalid mmWave coordinates.")

        timestamp = utc_now_iso()
        resolved_zone = zone_service.resolve_zone(data.x, data.y, data.zone)
        normalized = data.model_copy(update={"zone": resolved_zone})
        payload = normalized.model_dump()

        feature_vector = feature_service.build_mmwave_feature_vector(normalized)
        status = state_service.process_mmwave_event(
            detected=normalized.detected,
            zone=normalized.zone,
            motion_level=normalized.motion_level,
            still_time=normalized.still_time,
        )
        active_session = session_service.record_presence(
            detected=normalized.detected,
            zone=normalized.zone,
        )
        fall_result = fall_detector.evaluate(
            detected=normalized.detected,
            x=normalized.x,
            y=normalized.y,
            z=normalized.z,
            velocity=normalized.velocity,
            still_time=normalized.still_time,
        )
        speaker_result = None
        if fall_result["detected"]:
            status = state_service.mark_possible_fall_detected(
                score=fall_result["score"],
                reason=fall_result["reason"],
            )
            speaker_result = device_service.trigger_speaker(
                SpeakerRequest(
                    message="낙상이 감지되었습니다. 괜찮으시면 안전 확인 버튼을 눌러주세요.",
                    alert_level="danger",
                    repeat=3,
                )
            )

        anomaly_result = anomaly_service.analyze_mmwave(
            feature_vector=feature_vector,
            status=status,
            source="mmwave",
        )
        fusion_result = fusion_detector.evaluate(
            fall_result=fall_result,
            anomaly_prediction=anomaly_result,
            status=status,
        )

        result = {
            "timestamp": timestamp,
            "received": True,
            "sensor": "mmwave",
            "payload": payload,
            "feature_vector": feature_vector.model_dump(),
            "fall_detection": fall_result,
            "speaker_request": speaker_result,
            "anomaly": anomaly_result.model_dump(),
            "fusion_detection": fusion_result,
            "status": status.model_dump(),
            "session": active_session.model_dump() if active_session else None,
        }
        sensor_record = sensor_repository.save_mmwave(
            timestamp=timestamp,
            payload=payload,
            session_id=active_session.session_id if active_session else None,
            feature_vector=feature_vector.model_dump(),
            anomaly=anomaly_result.model_dump(),
            fall_detection=fall_result,
            status=status.model_dump(),
        )
        feature_repository.save(
            feature_vector=feature_vector,
            timestamp=timestamp,
            sensor_record_id=sensor_record["id"],
            session_id=active_session.session_id if active_session else None,
        )
        status_repository.save(status)

        self._remember_event("mmwave", result)
        log_service.add_log(
            log_type="sensor_service",
            message="mmWave event processed",
            data={
                "sensor": "mmwave",
                "resolved_zone": resolved_zone,
                "anomaly_detected": anomaly_result.detected,
                "fall_detected": fall_result["detected"],
                "current_state": status.current_state,
                "anomaly_reason": anomaly_result.reason,
            },
        )
        return result

    def receive_door(self, data: DoorSensorRequest) -> Dict[str, Any]:
        timestamp = utc_now_iso()
        payload = data.model_dump()
        status = state_service.process_door_event(door_state=data.door_state)
        completed_session = session_service.end_session() if data.door_state == "closed" else None

        result = {
            "timestamp": timestamp,
            "received": True,
            "sensor": "door",
            "payload": payload,
            "status": status.model_dump(),
            "session": completed_session.model_dump() if completed_session else None,
        }
        sensor_repository.save_door(
            timestamp=timestamp,
            payload=payload,
            session_id=completed_session.session_id if completed_session else None,
            status=status.model_dump(),
        )
        status_repository.save(status)

        self._remember_event("door", result)
        log_service.add_log(
            log_type="sensor_service",
            message="Door event processed",
            data={
                "sensor": "door",
                "door_state": data.door_state,
                "current_state": status.current_state,
            },
        )
        return result

    def get_last_events(self) -> Dict[str, Dict[str, Any]]:
        return self.last_events


sensor_service = SensorService()
