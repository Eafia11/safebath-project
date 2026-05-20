from datetime import datetime
from typing import Optional


def utc_now() -> datetime:
    return datetime.utcnow()


def utc_now_iso() -> str:
    return utc_now().isoformat()


def parse_iso_datetime(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def seconds_between(start: datetime, end: datetime | None = None, digits: int = 3) -> float:
    actual_end = end or utc_now()
    return round((actual_end - start).total_seconds(), digits)
