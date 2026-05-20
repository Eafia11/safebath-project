from datetime import datetime
from typing import Dict

from ..models.device import ButtonRequest, DeviceState, HeartbeatRequest, SpeakerRequest
from ..repositories.device_repository import device_repository
from ..repositories.status_repository import status_repository
from .log_service import log_service
from .state_service import state_service


class DeviceService:
    def __init__(self):
        self.devices: Dict[str, DeviceState] = {
            "mmwave": DeviceState(device_name="mmwave", status="online"),
            "door_sensor": DeviceState(device_name="door_sensor", status="online"),
            "button": DeviceState(device_name="button", status="online"),
            "speaker": DeviceState(device_name="speaker", status="online"),
        }
        for device_state in self.devices.values():
            device_repository.save(device_state)

    def _update_device(self, device_name: str, status: str, payload: dict | None = None) -> DeviceState:
        device_state = self.devices.get(device_name) or DeviceState(
            device_name=device_name,
            status=status,
        )
        device_state.status = status
        device_state.last_seen_at = datetime.utcnow().isoformat()
        device_state.last_payload = payload
        self.devices[device_name] = device_state
        device_repository.save(device_state)
        return device_state

    def process_button(self, data: ButtonRequest) -> dict:
        device_state = self._update_device(
            device_name="button",
            status="online",
            payload=data.model_dump(),
        )
        status = state_service.process_button_event(button_type=data.button_type)
        status_repository.save(status)

        log_service.add_log(
            log_type="device_service",
            message="Button event processed",
            data={
                "device": "button",
                "button_type": data.button_type,
                "current_state": status.current_state,
            },
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "received": True,
            "device": "button",
            "payload": data.model_dump(),
            "device_state": device_state.model_dump(),
            "status": status.model_dump(),
        }

    def trigger_speaker(self, data: SpeakerRequest) -> dict:
        device_state = self._update_device(
            device_name="speaker",
            status="online",
            payload=data.model_dump(),
        )

        log_service.add_log(
            log_type="device_service",
            message="Speaker request processed",
            data={
                "device": "speaker",
                "alert_level": data.alert_level,
                "repeat": data.repeat,
            },
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "requested": True,
            "device": "speaker",
            "payload": data.model_dump(),
            "device_state": device_state.model_dump(),
        }

    def receive_heartbeat(self, data: HeartbeatRequest) -> dict:
        device_state = self._update_device(
            device_name=data.device_name,
            status=data.status,
            payload=data.model_dump(),
        )

        log_service.add_log(
            log_type="device_service",
            message="Device heartbeat received",
            data=device_state.model_dump(),
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "received": True,
            "device": data.device_name,
            "device_state": device_state.model_dump(),
        }

    def get_devices(self) -> list[dict]:
        return [device.model_dump() for device in self.devices.values()]


device_service = DeviceService()
