from typing import Any, Dict, List, Optional


class SensorRepository:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self._next_id = 1

    def save_mmwave(
        self,
        timestamp: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        feature_vector: Optional[Dict[str, Any]] = None,
        anomaly: Optional[Dict[str, Any]] = None,
        fall_detection: Optional[Dict[str, Any]] = None,
        status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": self._next_id,
            "timestamp": timestamp,
            "sensor": "mmwave",
            "session_id": session_id,
            "x": payload.get("x"),
            "y": payload.get("y"),
            "z": payload.get("z"),
            "payload": payload,
            "feature_vector": feature_vector,
            "anomaly": anomaly,
            "fall_detection": fall_detection,
            "status": status,
        }
        self._next_id += 1
        self.records.append(record)
        return record

    def save_door(
        self,
        timestamp: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": self._next_id,
            "timestamp": timestamp,
            "sensor": "door",
            "session_id": session_id,
            "payload": payload,
            "status": status,
        }
        self._next_id += 1
        self.records.append(record)
        return record

    def list_records(self, sensor: Optional[str] = None) -> List[Dict[str, Any]]:
        if sensor is None:
            return self.records
        return [record for record in self.records if record["sensor"] == sensor]

    def get_latest(self, sensor: Optional[str] = None) -> Optional[Dict[str, Any]]:
        records = self.list_records(sensor=sensor)
        if not records:
            return None
        return records[-1]

    def recent_mmwave_points(self, limit: int) -> List[Dict[str, float]]:
        records = self.list_records(sensor="mmwave")
        points: List[Dict[str, float]] = []
        for record in reversed(records):
            payload = record.get("payload") or {}
            if not payload.get("detected"):
                continue

            x = payload.get("x")
            y = payload.get("y")
            if x is None or y is None:
                continue

            points.append({"x": float(x), "y": float(y)})
            if len(points) >= limit:
                break

        return list(reversed(points))

    def clear(self):
        self.records.clear()
        self._next_id = 1


sensor_repository = SensorRepository()
