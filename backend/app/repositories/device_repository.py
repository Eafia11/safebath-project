from typing import Dict, List, Optional

from ..models.device import DeviceState


class DeviceRepository:
    def __init__(self):
        self.devices: Dict[str, DeviceState] = {}

    def save(self, device_state: DeviceState) -> DeviceState:
        stored_device = device_state.model_copy()
        self.devices[stored_device.device_name] = stored_device
        return stored_device

    def get(self, device_name: str) -> Optional[DeviceState]:
        return self.devices.get(device_name)

    def list_devices(self) -> List[DeviceState]:
        return list(self.devices.values())

    def clear(self):
        self.devices.clear()


device_repository = DeviceRepository()
