from typing import List, Optional

from ..models.status import StatusSnapshot


class StatusRepository:
    def __init__(self):
        self.snapshots: List[StatusSnapshot] = []

    def save(self, snapshot: StatusSnapshot) -> StatusSnapshot:
        stored_snapshot = snapshot.model_copy()
        self.snapshots.append(stored_snapshot)
        return stored_snapshot

    def list_snapshots(self) -> List[StatusSnapshot]:
        return self.snapshots

    def get_latest(self) -> Optional[StatusSnapshot]:
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def clear(self):
        self.snapshots.clear()


status_repository = StatusRepository()
