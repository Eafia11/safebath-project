import argparse
import csv
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from random import Random
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data" / "demo"

# Demo coordinates are based on the latest LD2450 calibration runs in the scale model.
# Values are meters in the backend/app coordinate space.
ZONE_PROFILES = {
    "toilet": {"center_x": 0.12, "center_y": 0.686, "z": 1.08, "motion": 0.08, "radius": 0.09},
    "sink": {"center_x": -0.17, "center_y": 0.522, "z": 1.18, "motion": 0.12, "radius": 0.08},
    "bath": {"center_x": -0.247, "center_y": 0.725, "z": 1.02, "motion": 0.1, "radius": 0.1},
}

FIELDNAMES = [
    "timestamp",
    "scenario",
    "detected",
    "x",
    "y",
    "z",
    "zone",
    "motion_level",
    "velocity",
    "still_time",
    "current_state",
    "anomaly_detected",
    "anomaly_score",
    "anomaly_reason",
    "fall_detected",
    "fall_score",
    "fall_reason",
    "emergency_source",
]


def iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def make_row(
    *,
    timestamp: datetime,
    scenario: str,
    detected: bool,
    x: float | None,
    y: float | None,
    z: float | None,
    zone: str | None,
    motion_level: float,
    velocity: float,
    still_time: int,
    current_state: str,
    anomaly_detected: bool = False,
    anomaly_score: float = 0.0,
    anomaly_reason: str | None = None,
    fall_detected: bool = False,
    fall_score: float = 0.0,
    fall_reason: str | None = None,
    emergency_source: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": iso(timestamp),
        "scenario": scenario,
        "detected": detected,
        "x": x,
        "y": y,
        "z": z,
        "zone": zone,
        "motion_level": motion_level,
        "velocity": velocity,
        "still_time": still_time,
        "current_state": current_state,
        "anomaly_detected": anomaly_detected,
        "anomaly_score": anomaly_score,
        "anomaly_reason": anomaly_reason,
        "fall_detected": fall_detected,
        "fall_score": fall_score,
        "fall_reason": fall_reason,
        "emergency_source": emergency_source,
    }


def zone_point(random: Random, zone: str) -> tuple[float, float, float]:
    profile = ZONE_PROFILES[zone]
    jitter = profile["radius"] * 0.65
    x = round(profile["center_x"] + random.uniform(-jitter, jitter), 4)
    y = round(profile["center_y"] + random.uniform(-jitter, jitter), 4)
    z = round(profile["z"] + random.uniform(-0.04, 0.04), 4)
    return x, y, z


def normal_zone_rows(
    random: Random,
    start: datetime,
    zone: str,
    scenario: str,
    duration_minutes: int,
) -> list[dict[str, Any]]:
    profile = ZONE_PROFILES[zone]
    rows: list[dict[str, Any]] = []
    for minute in range(duration_minutes):
        x, y, z = zone_point(random, zone)
        still_time = max(0, minute * 60 + random.randint(-10, 20))
        rows.append(
            make_row(
                timestamp=start + timedelta(minutes=minute),
                scenario=scenario,
                detected=True,
                x=x,
                y=y,
                z=z,
                zone=zone,
                motion_level=round(max(profile["motion"] + random.uniform(-0.03, 0.06), 0.01), 4),
                velocity=round(random.uniform(0.02, 0.28), 4),
                still_time=still_time,
                current_state="TOILET_USE" if zone == "toilet" else "ACTIVE",
                anomaly_score=round(random.uniform(0.01, 0.18), 4),
            )
        )
    return rows


def empty_row(timestamp: datetime) -> dict[str, Any]:
    return make_row(
        timestamp=timestamp,
        scenario="empty_room",
        detected=False,
        x=None,
        y=None,
        z=None,
        zone=None,
        motion_level=0.0,
        velocity=0.0,
        still_time=0,
        current_state="EMPTY",
        anomaly_score=0.0,
    )


def build_rows(days: int, seed: int, start_date: datetime) -> list[dict[str, Any]]:
    random = Random(seed)
    rows: list[dict[str, Any]] = []

    for day_index in range(days):
        day = start_date + timedelta(days=day_index)
        rows.append(empty_row(day.replace(hour=5, minute=40, second=0)))

        rows.extend(
            normal_zone_rows(
                random,
                day.replace(hour=7, minute=random.randint(12, 25), second=0),
                "toilet",
                "morning_toilet",
                duration_minutes=random.randint(7, 11),
            )
        )
        rows.extend(
            normal_zone_rows(
                random,
                day.replace(hour=7, minute=random.randint(28, 38), second=0),
                "sink",
                "morning_sink",
                duration_minutes=random.randint(4, 7),
            )
        )

        rows.extend(
            normal_zone_rows(
                random,
                day.replace(hour=20, minute=random.randint(30, 50), second=0),
                "bath",
                "evening_bath",
                duration_minutes=random.randint(10, 16),
            )
        )

        if day_index % 7 in {1, 5}:
            rows.extend(
                normal_zone_rows(
                    random,
                    day.replace(hour=23, minute=random.randint(10, 45), second=0),
                    "toilet",
                    "night_toilet",
                    duration_minutes=random.randint(3, 6),
                )
            )

        rows.append(empty_row(day.replace(hour=23, minute=59, second=0)))

    rows.sort(key=lambda row: row["timestamp"])
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def post_records(backend_url: str, rows: list[dict[str, Any]], clear_existing: bool, api_key: str) -> dict[str, Any]:
    url = backend_url.rstrip("/") + "/admin/demo/mmwave"
    payload = json.dumps(
        {"clear_existing": clear_existing, "records": rows},
        ensure_ascii=False,
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload failed: HTTP {error.code} {body}") from error


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SafeBath demo mmWave data.")
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD. Defaults to days-1 before today.")
    parser.add_argument("--output", default=None)
    parser.add_argument("--backend-url", default=None, help="Upload target, for example http://43.201.28.192:8000")
    parser.add_argument("--api-key", default=os.getenv("SAFEBATH_API_KEY", os.getenv("API_KEY", "")))
    parser.add_argument("--clear-existing", action="store_true")
    args = parser.parse_args()

    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    else:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=args.days - 1)

    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / "mmwave_demo_21d.csv"
    rows = build_rows(days=args.days, seed=args.seed, start_date=start_date)
    write_csv(output_path, rows)

    anomaly_count = sum(1 for row in rows if row["anomaly_detected"])
    fall_count = sum(1 for row in rows if row["fall_detected"])
    emergency_count = sum(1 for row in rows if row["current_state"] == "EMERGENCY")

    print(f"Generated {len(rows)} rows.")
    print(f"- days: {args.days}")
    print(f"- anomaly rows: {anomaly_count}")
    print(f"- fall rows: {fall_count}")
    print(f"- emergency rows: {emergency_count}")
    print(f"- output: {output_path}")

    if args.backend_url:
        result = post_records(args.backend_url, rows, args.clear_existing, args.api_key)
        print(f"Uploaded to {args.backend_url}")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
