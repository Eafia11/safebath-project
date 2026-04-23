from datetime import datetime
from typing import Any, Dict

from ..models.sensor import DoorSensorRequest, MmWaveSensorRequest
from .anomaly_service import anomaly_service
from .feature_service import feature_service
from .log_service import log_service
from .state_service import state_service


class SensorService:
    def __init__(self):
        self.last_events: Dict[str, Dict[str, Any]] = {}

    def _remember_event(self, sensor_name: str, payload: Dict[str, Any]):
        self.last_events[sensor_name] = {
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }

    def receive_mmwave(self, data: MmWaveSensorRequest) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        payload = data.model_dump()

        feature_vector = feature_service.build_mmwave_feature_vector(data)
        status = state_service.process_mmwave_event(
            detected=data.detected,
            zone=data.zone,
            motion_level=data.motion_level,
            still_time=data.still_time,
        )
        anomaly_result = anomaly_service.analyze_mmwave(
            feature_vector=feature_vector,
            status=status,
            source="mmwave",
        )

        result = {
            "timestamp": timestamp,
            "received": True,
            "sensor": "mmwave",
            "payload": payload,
            "feature_vector": feature_vector.model_dump(),
            "anomaly": anomaly_result.model_dump(),
            "status": status.model_dump(),
        }

        self._remember_event("mmwave", result)
        log_service.add_log(
            log_type="sensor_service",
            message="mmWave event processed",
            data={
                "sensor": "mmwave",
                "anomaly_detected": anomaly_result.detected,
                "current_state": status.current_state,
                "anomaly_reason": anomaly_result.reason,
            },
        )
        return result

    def receive_door(self, data: DoorSensorRequest) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        payload = data.model_dump()
        status = state_service.process_door_event(door_state=data.door_state)

        result = {
            "timestamp": timestamp,
            "received": True,
            "sensor": "door",
            "payload": payload,
            "status": status.model_dump(),
        }

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
