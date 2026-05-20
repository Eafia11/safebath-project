import sys
from pathlib import Path
from random import Random


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.db.init_db import init_db
from backend.app.models.sensor import DoorSensorRequest, MmWaveSensorRequest
from backend.app.services.sensor_service import sensor_service


ZONE_PROFILES = {
    "door": {"center_x": 0.3, "center_y": 0.4, "z": 1.45, "motion": 0.18},
    "sink": {"center_x": 1.2, "center_y": 0.8, "z": 1.35, "motion": 0.12},
    "toilet": {"center_x": 2.0, "center_y": 1.4, "z": 1.2, "motion": 0.08},
}


def _normal_sample(random: Random, zone_name: str, index: int) -> dict:
    profile = ZONE_PROFILES[zone_name]
    return {
        "detected": True,
        "x": round(profile["center_x"] + random.uniform(-0.18, 0.18), 3),
        "y": round(profile["center_y"] + random.uniform(-0.18, 0.18), 3),
        "z": round(profile["z"] + random.uniform(-0.08, 0.08), 3),
        "motion_level": round(max(profile["motion"] + random.uniform(-0.04, 0.08), 0.01), 3),
        "velocity": round(random.uniform(0.02, 0.35), 3),
        "still_time": random.randint(0, 8 if zone_name != "toilet" else 14),
        "zone": zone_name,
    }


def _transition_sample(random: Random, index: int) -> dict:
    return {
        "detected": True,
        "x": round(0.4 + index * 0.08 + random.uniform(-0.05, 0.05), 3),
        "y": round(0.5 + index * 0.04 + random.uniform(-0.05, 0.05), 3),
        "z": round(1.4 + random.uniform(-0.05, 0.05), 3),
        "motion_level": round(random.uniform(0.2, 0.45), 3),
        "velocity": round(random.uniform(0.25, 0.7), 3),
        "still_time": random.randint(0, 3),
    }


def _empty_sample() -> dict:
    return {
        "detected": False,
        "x": None,
        "y": None,
        "z": None,
        "motion_level": 0.0,
        "velocity": 0.0,
        "still_time": 0,
    }


def build_dummy_mmwave_samples(seed: int = 42) -> list[dict]:
    random = Random(seed)
    samples = []
    for zone_name in ZONE_PROFILES:
        for index in range(15):
            samples.append(_normal_sample(random, zone_name, index))

    for index in range(10):
        samples.append(_transition_sample(random, index))

    for _ in range(5):
        samples.append(_empty_sample())

    samples.extend(
        [
            {
                "detected": True,
                "x": 2.1,
                "y": 1.5,
                "z": 0.55,
                "motion_level": 0.0,
                "velocity": 1.3,
                "still_time": 35,
                "zone": "toilet",
            },
            {
                "detected": True,
                "x": 3.2,
                "y": 2.8,
                "z": 0.8,
                "motion_level": 0.02,
                "velocity": 1.0,
                "still_time": 45,
            },
        ]
    )
    return samples


def main():
    init_db()
    samples = build_dummy_mmwave_samples()
    sensor_service.receive_door(DoorSensorRequest(door_state="open"))
    for sample in samples:
        sensor_service.receive_mmwave(MmWaveSensorRequest(**sample))
    sensor_service.receive_door(DoorSensorRequest(door_state="closed"))
    print(f"Seeded {len(samples)} dummy mmWave samples.")


if __name__ == "__main__":
    main()
