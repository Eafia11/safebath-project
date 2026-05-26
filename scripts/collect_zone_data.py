import argparse
import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT_DIR / "data" / "raw"
DEFAULT_LABELS = [
    "empty",
    "toilet",
    "sink",
    "bath",
    "toilet_to_sink",
    "toilet_to_bath",
    "abnormal",
]


def utc_now() -> datetime:
    return datetime.utcnow()


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def parse_server_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def get_json(url: str, api_key: str | None) -> dict:
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_tuning_records(backend_url: str, api_key: str | None, limit: int) -> list[dict]:
    url = f"{backend_url.rstrip('/')}/admin/tuning?limit={limit}"
    payload = get_json(url, api_key)
    return payload.get("data", {}).get("records", [])


def wait_segment(label: str, duration: int) -> tuple[datetime, datetime]:
    input(f"\n[{label}] target을 배치한 뒤 Enter를 누르세요. {duration}초 동안 수집합니다.")
    started_at = utc_now()
    print(f"[{label}] start: {iso(started_at)} UTC")
    for remaining in range(duration, 0, -1):
        print(f"\r[{label}] remaining: {remaining:3d}s", end="", flush=True)
        time.sleep(1)
    ended_at = utc_now()
    print(f"\r[{label}] done: {iso(ended_at)} UTC{' ' * 12}")
    return started_at, ended_at


def label_records(records: list[dict], segments: list[dict]) -> list[dict]:
    labeled = []
    for record in records:
        timestamp = parse_server_timestamp(record.get("timestamp"))
        if timestamp is None:
            continue

        matched_segment = None
        for segment in segments:
            if segment["started_at"] <= timestamp <= segment["ended_at"]:
                matched_segment = segment
                break

        if not matched_segment:
            continue

        row = {
            "label": matched_segment["label"],
            "segment_started_at": iso(matched_segment["started_at"]),
            "segment_ended_at": iso(matched_segment["ended_at"]),
        }
        row.update(record)
        labeled.append(row)
    return labeled


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "label",
        "segment_started_at",
        "segment_ended_at",
        "id",
        "timestamp",
        "session_id",
        "detected",
        "x",
        "y",
        "z",
        "zone",
        "motion_level",
        "velocity",
        "still_time",
        "current_state",
        "waiting_for_response",
        "pending_response_type",
        "fall_detected",
        "fall_score",
        "height_drop",
        "speed_change",
        "anomaly_detected",
        "anomaly_score",
        "anomaly_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> None:
    print("\nSummary")
    if not rows:
        print("- no labeled records found")
        return

    counts: dict[str, int] = {}
    detected_counts: dict[str, int] = {}
    for row in rows:
        label = row["label"]
        counts[label] = counts.get(label, 0) + 1
        if row.get("detected") in (True, "True", "true", 1, "1"):
            detected_counts[label] = detected_counts.get(label, 0) + 1

    for label in sorted(counts):
        print(f"- {label}: {counts[label]} records, detected={detected_counts.get(label, 0)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect labeled zone data from backend /admin/tuning records.",
    )
    parser.add_argument(
        "--backend-url",
        default=os.getenv("SAFEBATH_BACKEND_URL", "http://43.201.28.192:8000"),
        help="SafeBath backend URL.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("SAFEBATH_API_KEY", os.getenv("API_KEY", "")),
        help="API key for /admin/tuning if configured.",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        default=DEFAULT_LABELS,
        help="Labels to collect in order.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Seconds to collect each label.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Number of recent tuning records to fetch after collection.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path. Defaults to data/raw/zone_collection_<timestamp>.csv.",
    )
    args = parser.parse_args()

    output_path = (
        Path(args.output)
        if args.output
        else DEFAULT_OUTPUT_DIR / f"zone_collection_{utc_now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    print("Zone data collection")
    print(f"- backend: {args.backend_url}")
    print(f"- labels: {', '.join(args.labels)}")
    print(f"- duration: {args.duration}s per label")
    print(f"- output: {output_path}")
    print("\n먼저 백엔드와 iot/ld2450_sender.py가 실행 중인지 확인하세요.")

    try:
        get_json(f"{args.backend_url.rstrip('/')}/health", args.api_key or None)
    except (HTTPError, URLError, TimeoutError) as error:
        raise SystemExit(f"Backend health check failed: {error}") from error

    segments = []
    for label in args.labels:
        started_at, ended_at = wait_segment(label, args.duration)
        segments.append({"label": label, "started_at": started_at, "ended_at": ended_at})

    print("\nFetching tuning records...")
    try:
        records = fetch_tuning_records(args.backend_url, args.api_key or None, args.limit)
    except (HTTPError, URLError, TimeoutError) as error:
        raise SystemExit(f"Failed to fetch tuning records: {error}") from error

    labeled_rows = label_records(records, segments)
    write_csv(output_path, labeled_rows)
    summarize(labeled_rows)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
