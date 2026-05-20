from math import sqrt
from typing import Optional


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def safe_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def distance_2d(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def distance_3d(
    x1: Optional[float],
    y1: Optional[float],
    z1: Optional[float],
    x2: Optional[float],
    y2: Optional[float],
    z2: Optional[float],
) -> Optional[float]:
    if None in {x1, y1, z1, x2, y2, z2}:
        return None
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
