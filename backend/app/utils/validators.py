from typing import Optional


VALID_ZONE_NAMES = {"toilet", "sink", "bath"}


def is_valid_coordinate(value: Optional[float]) -> bool:
    return value is None or isinstance(value, (int, float))


def validate_mmwave_coordinates(
    x: Optional[float],
    y: Optional[float],
    z: Optional[float] = None,
) -> bool:
    return all(is_valid_coordinate(value) for value in (x, y, z))


def validate_zone_name(zone_name: Optional[str]) -> bool:
    return zone_name is None or zone_name in VALID_ZONE_NAMES
