import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


ZONE_LABELS = {"toilet", "sink", "bath"}


def parse_float(value: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_bool(value: str) -> bool:
    return str(value).lower() in {"true", "1", "yes"}


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * ratio)))
    return ordered[index]


def row_points(rows: list[dict]) -> list[tuple[float, float]]:
    points = []
    for row in rows:
        if not parse_bool(row.get("detected", "")):
            continue
        x = parse_float(row.get("x"))
        y = parse_float(row.get("y"))
        if x is None or y is None:
            continue
        points.append((x, y))
    return points


def distance_to_nearest(point: tuple[float, float], candidates: list[tuple[float, float]]) -> float | None:
    if not candidates:
        return None
    return min(math.hypot(point[0] - x, point[1] - y) for x, y in candidates)


def remove_empty_noise(
    label: str,
    points: list[tuple[float, float]],
    empty_points: list[tuple[float, float]],
    radius: float,
) -> list[tuple[float, float]]:
    if label == "empty" or radius <= 0 or not empty_points:
        return points
    return [
        point
        for point in points
        if (distance_to_nearest(point, empty_points) or float("inf")) > radius
    ]


def print_point_stats(label: str, points: list[tuple[float, float]], padding: float) -> dict | None:
    if not points:
        return None

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    center_x = mean(xs)
    center_y = mean(ys)
    distances = [math.hypot(x - center_x, y - center_y) for x, y in points]
    radius_p90 = percentile(distances, 0.90)
    radius_max = max(distances)
    suggested_radius = max(0.03, radius_p90 + padding)

    print(
        "  "
        f"x={min(xs):.3f}~{max(xs):.3f}, "
        f"y={min(ys):.3f}~{max(ys):.3f}, "
        f"avg=({center_x:.3f}, {center_y:.3f}), "
        f"radius_p90={radius_p90:.3f}, radius_max={radius_max:.3f}, "
        f"suggested_radius={suggested_radius:.3f}"
    )
    return {
        "center_x": center_x,
        "center_y": center_y,
        "radius": suggested_radius,
    }


def analyze(path: Path, padding: float, margin: float, empty_noise_radius: float) -> None:
    groups: dict[str, list[dict]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            groups[row.get("label", "unknown")].append(row)

    print(f"File: {path}")
    print()
    print("Label summary")

    all_x: list[float] = []
    all_y: list[float] = []
    zone_suggestions = {}
    empty_points = row_points(groups.get("empty", []))

    for label in sorted(groups):
        rows = groups[label]
        detected_rows = [row for row in rows if parse_bool(row.get("detected", ""))]
        raw_points = row_points(detected_rows)
        filtered_points = remove_empty_noise(label, raw_points, empty_points, empty_noise_radius)
        for x, y in filtered_points:
            all_x.append(x)
            all_y.append(y)

        removed = len(raw_points) - len(filtered_points)
        suffix = f", noise_removed={removed}" if empty_noise_radius > 0 and label != "empty" else ""
        print(
            f"- {label}: total={len(rows)}, detected={len(detected_rows)}, "
            f"points={len(raw_points)}, used={len(filtered_points)}{suffix}"
        )

        if not filtered_points:
            continue

        stats = print_point_stats(label, filtered_points, padding)

        if label in ZONE_LABELS and stats:
            zone_suggestions[label] = stats

    print()
    if all_x and all_y:
        space_x_min = min(all_x) - margin
        space_x_max = max(all_x) + margin
        space_y_min = min(all_y) - margin
        space_y_max = max(all_y) + margin
        roi_x_limit = max(abs(space_x_min), abs(space_x_max))

        print("Suggested sender bounds")
        print(f"- LD2450_SPACE_X_MIN={round(space_x_min * 1000)}")
        print(f"- LD2450_SPACE_X_MAX={round(space_x_max * 1000)}")
        print(f"- LD2450_SPACE_Y_MIN={round(space_y_min * 1000)}")
        print(f"- LD2450_SPACE_Y_MAX={round(space_y_max * 1000)}")
        print(f"- LD2450_ROI_X_LIMIT={round(roi_x_limit * 1000)}")
        print(f"- LD2450_ROI_Y_MIN={round(space_y_min * 1000)}")
        print(f"- LD2450_ROI_Y_MAX={round(space_y_max * 1000)}")
    else:
        print("No detected x/y points found.")

    print()
    print("Suggested calibration commands")
    if zone_suggestions:
        print('curl -X POST http://10.112.131.178:8000/calibration/start -H "Content-Type: application/json" -d "{\\"user_id\\":\\"zone_collection\\"}"')
    for zone_name in ("toilet", "sink", "bath"):
        zone = zone_suggestions.get(zone_name)
        if not zone:
            print(f"# {zone_name}: no points")
            continue
        body = (
            "{"
            f'\\"zone_name\\":\\"{zone_name}\\",'
            f'\\"center_x\\":{zone["center_x"]:.4f},'
            f'\\"center_y\\":{zone["center_y"]:.4f},'
            f'\\"radius\\":{zone["radius"]:.4f}'
            "}"
        )
        print(
            "curl -X POST http://10.112.131.178:8000/calibration/complete "
            f'-H "Content-Type: application/json" -d "{body}"'
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze labeled SafeBath zone collection CSV.")
    parser.add_argument("csv_path", help="Path to zone_collection_*.csv")
    parser.add_argument("--padding", type=float, default=0.04, help="Extra radius padding in meters.")
    parser.add_argument("--margin", type=float, default=0.08, help="Extra sender bound margin in meters.")
    parser.add_argument(
        "--empty-noise-radius",
        type=float,
        default=0.0,
        help="Remove non-empty points within this distance in meters from any empty point.",
    )
    args = parser.parse_args()

    analyze(
        Path(args.csv_path),
        padding=args.padding,
        margin=args.margin,
        empty_noise_radius=args.empty_noise_radius,
    )


if __name__ == "__main__":
    main()
