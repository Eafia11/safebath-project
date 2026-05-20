from typing import Any, Dict, List, Optional

from ..models.feature import FeatureVector


class FeatureRepository:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self._next_id = 1

    def save(
        self,
        feature_vector: FeatureVector,
        timestamp: str,
        source: str = "mmwave",
        sensor_record_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = {
            "id": self._next_id,
            "timestamp": timestamp,
            "source": source,
            "sensor_record_id": sensor_record_id,
            "session_id": session_id,
            "feature_vector": feature_vector.model_dump(),
        }
        self._next_id += 1
        self.records.append(record)
        return record

    def list_records(self) -> List[Dict[str, Any]]:
        return self.records

    def get_latest(self) -> Optional[Dict[str, Any]]:
        if not self.records:
            return None
        return self.records[-1]

    def clear(self):
        self.records.clear()
        self._next_id = 1


feature_repository = FeatureRepository()
