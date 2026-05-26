import argparse
import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import serial


FRAME_HEADER = b"\xAA\xFF\x03\x00"
FRAME_FOOTER = b"\x55\xCC"
FRAME_LENGTH = 30
TARGET_COUNT = 3
TARGET_BYTES = 8

BACKEND_URL = os.getenv("SAFEBATH_BACKEND_URL", "http://43.201.28.192:8000")
API_KEY = os.getenv("SAFEBATH_API_KEY", "")

# Default target filters for the 60 x 60 x 60cm demo model.
DEFAULT_ROI_Y_MIN = 0
DEFAULT_ROI_Y_MAX = 600
DEFAULT_ROI_X_LIMIT = 300
DEFAULT_SPACE_X_MIN = -300
DEFAULT_SPACE_X_MAX = 300
DEFAULT_SPACE_Y_MIN = 0
DEFAULT_SPACE_Y_MAX = 600
DEFAULT_MAX_SPEED_CM_S = 150
DEFAULT_STALE_SECONDS = 3.0
DEFAULT_WARMUP_SECONDS = 2.0


@dataclass
class Target:
    x_mm: int
    y_mm: int
    speed_cm_s: int
    resolution_mm: int

    @property
    def active(self) -> bool:
        return any((self.x_mm, self.y_mm, self.speed_cm_s, self.resolution_mm))

    @property
    def distance_mm(self) -> float:
        return math.hypot(self.x_mm, self.y_mm)


@dataclass
class SlotState:
    signature: tuple[int, int, int, int] | None = None
    unchanged_since: float = 0.0


def decode_signed(raw: int) -> int:
    # LD2450 uses the high bit as a direction flag: set means positive.
    return raw - 0x8000 if raw & 0x8000 else -raw


def parse_frame(frame: bytes) -> list[Target]:
    if len(frame) != FRAME_LENGTH:
        raise ValueError(f"Invalid LD2450 frame length: {len(frame)}")
    if not frame.startswith(FRAME_HEADER) or not frame.endswith(FRAME_FOOTER):
        raise ValueError("Invalid LD2450 frame boundary")

    payload = frame[4:-2]
    targets = []
    for index in range(TARGET_COUNT):
        offset = index * TARGET_BYTES
        chunk = payload[offset : offset + TARGET_BYTES]
        x_raw = int.from_bytes(chunk[0:2], "little")
        y_raw = int.from_bytes(chunk[2:4], "little")
        speed_raw = int.from_bytes(chunk[4:6], "little")
        resolution = int.from_bytes(chunk[6:8], "little")
        targets.append(
            Target(
                x_mm=decode_signed(x_raw),
                y_mm=decode_signed(y_raw),
                speed_cm_s=decode_signed(speed_raw),
                resolution_mm=resolution,
            )
        )
    return targets


def iter_frames(port: serial.Serial) -> Iterable[bytes]:
    buffer = bytearray()
    while True:
        buffer.extend(port.read(port.in_waiting or 1))
        while True:
            header_index = buffer.find(FRAME_HEADER)
            if header_index < 0:
                del buffer[:-3]
                break
            if header_index:
                del buffer[:header_index]
            if len(buffer) < FRAME_LENGTH:
                break
            frame = bytes(buffer[:FRAME_LENGTH])
            del buffer[:FRAME_LENGTH]
            if frame.endswith(FRAME_FOOTER):
                yield frame


def post_json(path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    request = Request(f"{BACKEND_URL}{path}", data=body, headers=headers, method="POST")
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def target_signature(target: Target) -> tuple[int, int, int, int]:
    return (target.x_mm, target.y_mm, target.speed_cm_s, target.resolution_mm)


def update_slot_states(targets: list[Target], slot_states: list[SlotState], now: float) -> None:
    for target, state in zip(targets, slot_states):
        if not target.active:
            state.signature = None
            state.unchanged_since = now
            continue

        signature = target_signature(target)
        if signature != state.signature:
            state.signature = signature
            state.unchanged_since = now


def unchanged_age(index: int, slot_states: list[SlotState], now: float) -> float:
    return now - slot_states[index - 1].unchanged_since


def is_stale(index: int, target: Target, slot_states: list[SlotState], now: float, stale_seconds: float) -> bool:
    return target.active and target.speed_cm_s == 0 and unchanged_age(index, slot_states, now) >= stale_seconds


def is_inside_space(target: Target, space: dict) -> bool:
    return (
        space["x_min"] <= target.x_mm <= space["x_max"]
        and space["y_min"] <= target.y_mm <= space["y_max"]
    )


def is_candidate(
    index: int,
    target: Target,
    roi: dict,
    space: dict,
    max_speed_cm_s: int,
    slot_states: list[SlotState],
    now: float,
    stale_seconds: float,
    enforce_roi: bool,
    enforce_space: bool,
    enforce_speed: bool,
) -> bool:
    return (
        (not enforce_roi or roi["y_min"] <= target.y_mm <= roi["y_max"])
        and (not enforce_roi or abs(target.x_mm) <= roi["x_limit"])
        and (not enforce_space or is_inside_space(target, space))
        and (not enforce_speed or abs(target.speed_cm_s) <= max_speed_cm_s)
        and not is_stale(index, target, slot_states, now, stale_seconds)
    )


def choose_primary_target(
    targets: list[Target],
    roi: dict,
    space: dict,
    max_speed_cm_s: int,
    slot_states: list[SlotState],
    now: float,
    stale_seconds: float,
    prefer_moving: bool = False,
    enforce_roi: bool = True,
    enforce_space: bool = True,
    enforce_speed: bool = True,
) -> tuple[int | None, Target | None]:
    candidates = [
        (index, target)
        for index, target in enumerate(targets, start=1)
        if target.active
        and is_candidate(
            index,
            target,
            roi,
            space,
            max_speed_cm_s,
            slot_states,
            now,
            stale_seconds,
            enforce_roi,
            enforce_space,
            enforce_speed,
        )
    ]
    if not candidates:
        return None, None

    if prefer_moving:
        moving = [candidate for candidate in candidates if abs(candidate[1].speed_cm_s) > 0]
        if moving:
            return max(moving, key=lambda item: abs(item[1].speed_cm_s))

    return min(candidates, key=lambda item: item[1].distance_mm)


def reject_reason(
    index: int,
    target: Target,
    roi: dict,
    space: dict,
    max_speed_cm_s: int,
    slot_states: list[SlotState],
    now: float,
    stale_seconds: float,
    enforce_space: bool,
) -> str:
    if not target.active:
        return "none"

    reasons = []
    if enforce_space and not is_inside_space(target, space):
        reasons.append("out_space")
    if not roi["y_min"] <= target.y_mm <= roi["y_max"]:
        reasons.append("out_y")
    if abs(target.x_mm) > roi["x_limit"]:
        reasons.append("out_x")
    if abs(target.speed_cm_s) > max_speed_cm_s:
        reasons.append("too_fast")
    if is_stale(index, target, slot_states, now, stale_seconds):
        reasons.append(f"stale_{unchanged_age(index, slot_states, now):.1f}s")
    return ",".join(reasons) if reasons else "ok"


def format_target(
    index: int,
    target: Target,
    roi: dict,
    space: dict,
    max_speed_cm_s: int,
    slot_states: list[SlotState],
    now: float,
    stale_seconds: float,
    enforce_space: bool,
    selected_index: int | None = None,
) -> str:
    if not target.active:
        return f"T{index}=none"
    reason = reject_reason(
        index,
        target,
        roi,
        space,
        max_speed_cm_s,
        slot_states,
        now,
        stale_seconds,
        enforce_space,
    )
    selected = "*" if index == selected_index else " "
    return (
        f"{selected}T{index}(x={target.x_mm / 1000.0:.3f}, "
        f"y={target.y_mm / 1000.0:.3f}, "
        f"v={target.speed_cm_s / 100.0:.2f}, "
        f"d={target.distance_mm / 1000.0:.3f}, "
        f"{reason})"
    )


def format_target_board(
    targets: list[Target],
    roi: dict,
    space: dict,
    max_speed_cm_s: int,
    slot_states: list[SlotState],
    now: float,
    stale_seconds: float,
    enforce_space: bool,
    selected_index: int | None,
) -> str:
    lines = [
        "  +--------+--------+--------+--------+----------+----------------+",
        "  | target | x(m)   | y(m)   | v(m/s) | dist(m)  | status         |",
        "  +--------+--------+--------+--------+----------+----------------+",
    ]
    for index, target in enumerate(targets, start=1):
        if not target.active:
            lines.append(f"  | T{index}     | none   | none   | none   | none     | none           |")
            continue

        reason = reject_reason(
            index,
            target,
            roi,
            space,
            max_speed_cm_s,
            slot_states,
            now,
            stale_seconds,
            enforce_space,
        )
        status = "selected" if index == selected_index else reason
        marker = "*" if index == selected_index else " "
        lines.append(
            f"  | {marker}T{index}    | "
            f"{target.x_mm / 1000.0:>6.3f} | "
            f"{target.y_mm / 1000.0:>6.3f} | "
            f"{target.speed_cm_s / 100.0:>6.2f} | "
            f"{target.distance_mm / 1000.0:>8.3f} | "
            f"{status[:14]:<14} |"
        )
    lines.append("  +--------+--------+--------+--------+----------+----------------+")
    return "\n".join(lines)


def format_raw_frame(frame: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in frame)


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read HLK-LD2450 UART data and send it to SafeBath backend.")
    parser.add_argument("--port", default=os.getenv("LD2450_PORT", "/dev/ttyUSB0"))
    parser.add_argument("--baud", type=int, default=int(os.getenv("LD2450_BAUD", "256000")))
    parser.add_argument("--interval", type=float, default=float(os.getenv("LD2450_SEND_INTERVAL", "0.3")))
    parser.add_argument("--debug-targets", action="store_true", help="Print all LD2450 targets for calibration.")
    parser.add_argument("--debug-raw", action="store_true", help="Print raw LD2450 frame bytes.")
    parser.add_argument("--no-post", action="store_true", help="Read and print sensor data without sending to backend.")
    parser.add_argument("--roi-y-min", type=int, default=int(os.getenv("LD2450_ROI_Y_MIN", str(DEFAULT_ROI_Y_MIN))))
    parser.add_argument("--roi-y-max", type=int, default=int(os.getenv("LD2450_ROI_Y_MAX", str(DEFAULT_ROI_Y_MAX))))
    parser.add_argument("--roi-x-limit", type=int, default=int(os.getenv("LD2450_ROI_X_LIMIT", str(DEFAULT_ROI_X_LIMIT))))
    parser.add_argument(
        "--space-x-min",
        type=int,
        default=int(os.getenv("LD2450_SPACE_X_MIN", str(DEFAULT_SPACE_X_MIN))),
        help="Minimum x coordinate in mm for the 60cm model space.",
    )
    parser.add_argument(
        "--space-x-max",
        type=int,
        default=int(os.getenv("LD2450_SPACE_X_MAX", str(DEFAULT_SPACE_X_MAX))),
        help="Maximum x coordinate in mm for the 60cm model space.",
    )
    parser.add_argument(
        "--space-y-min",
        type=int,
        default=int(os.getenv("LD2450_SPACE_Y_MIN", str(DEFAULT_SPACE_Y_MIN))),
        help="Minimum y coordinate in mm for the 60cm model space.",
    )
    parser.add_argument(
        "--space-y-max",
        type=int,
        default=int(os.getenv("LD2450_SPACE_Y_MAX", str(DEFAULT_SPACE_Y_MAX))),
        help="Maximum y coordinate in mm for the 60cm model space.",
    )
    parser.add_argument(
        "--max-speed-cm-s",
        type=int,
        default=int(os.getenv("LD2450_MAX_SPEED_CM_S", str(DEFAULT_MAX_SPEED_CM_S))),
    )
    parser.add_argument(
        "--stale-seconds",
        type=float,
        default=float(os.getenv("LD2450_STALE_SECONDS", str(DEFAULT_STALE_SECONDS))),
        help="Ignore a zero-speed target slot after the exact same value repeats for this many seconds.",
    )
    parser.add_argument(
        "--warmup-seconds",
        type=float,
        default=float(os.getenv("LD2450_WARMUP_SECONDS", str(DEFAULT_WARMUP_SECONDS))),
        help="Discard frames for this many seconds after opening the serial port.",
    )
    parser.add_argument("--prefer-moving", action="store_true", help="Prefer moving targets over the nearest one.")
    parser.add_argument(
        "--allow-out-of-roi",
        action="store_true",
        help="Show and send targets outside ROI. Useful when measuring real x/y bounds.",
    )
    parser.add_argument(
        "--allow-too-fast",
        action="store_true",
        help="Show and send targets even when speed exceeds max-speed-cm-s.",
    )
    parser.add_argument(
        "--allow-out-of-space",
        action="store_true",
        help="Show out-of-space targets but still allow them to be selected and sent.",
    )
    parser.add_argument(
        "--discovery-mode",
        action="store_true",
        help="Measure raw bounds: allow targets outside ROI, outside model space, and above speed limit.",
    )
    args = parser.parse_args()

    roi = {"y_min": args.roi_y_min, "y_max": args.roi_y_max, "x_limit": args.roi_x_limit}
    space = {
        "x_min": args.space_x_min,
        "x_max": args.space_x_max,
        "y_min": args.space_y_min,
        "y_max": args.space_y_max,
    }
    enforce_roi = not (args.allow_out_of_roi or args.discovery_mode)
    enforce_space = not (args.allow_out_of_space or args.discovery_mode)
    enforce_speed = not (args.allow_too_fast or args.discovery_mode)

    last_sent_at = 0.0
    still_started_at = time.monotonic()
    slot_states = [SlotState() for _ in range(TARGET_COUNT)]

    print(f"Reading LD2450 from {args.port} at {args.baud} baud")
    print(
        "Backend posting disabled (--no-post)"
        if args.no_post
        else f"Sending samples to {BACKEND_URL}/sensor/mmwave"
    )
    print(
        f"Target filter: y={roi['y_min']}~{roi['y_max']}mm, "
        f"|x|<={roi['x_limit']}mm, |speed|<={args.max_speed_cm_s}cm/s, "
        f"stale={args.stale_seconds}s, prefer_moving={args.prefer_moving}, "
        f"roi={'on' if enforce_roi else 'off'}, speed={'on' if enforce_speed else 'off'}"
    )
    print(
        f"Model space: x={space['x_min']}~{space['x_max']}mm, "
        f"y={space['y_min']}~{space['y_max']}mm, "
        f"out-of-space={'allowed' if args.allow_out_of_space else 'ignored'}"
    )

    with serial.Serial(args.port, args.baud, timeout=1) as port:
        port.reset_input_buffer()
        port.reset_output_buffer()
        opened_at = time.monotonic()
        print(f"Serial buffers reset. Warming up for {args.warmup_seconds:.1f}s...")
        for frame in iter_frames(port):
            now = time.monotonic()
            if now - last_sent_at < args.interval:
                continue

            targets = parse_frame(frame)
            update_slot_states(targets, slot_states, now)
            target_index, target = choose_primary_target(
                targets,
                roi,
                space,
                args.max_speed_cm_s,
                slot_states,
                now,
                args.stale_seconds,
                prefer_moving=args.prefer_moving,
                enforce_roi=enforce_roi,
                enforce_space=enforce_space,
                enforce_speed=enforce_speed,
            )
            detected = target is not None
            velocity = abs(target.speed_cm_s) / 100.0 if target else 0.0
            if detected and velocity > 0.03:
                still_started_at = now

            payload = {
                "detected": detected,
                "x": target.x_mm / 1000.0 if target else None,
                "y": target.y_mm / 1000.0 if target else None,
                "z": None,
                "motion_level": min(1.0, velocity) if detected else 0.0,
                "velocity": velocity,
                "still_time": int(now - still_started_at) if detected else 0,
                "zone": None,
            }

            if args.debug_raw:
                print(f"{timestamp()} raw={format_raw_frame(frame)}")

            if now - opened_at < args.warmup_seconds:
                if args.debug_targets:
                    print(f"{timestamp()} warmup frame ignored")
                    print(
                        format_target_board(
                            targets,
                            roi,
                            space,
                            args.max_speed_cm_s,
                            slot_states,
                            now,
                            args.stale_seconds,
                            enforce_space,
                            target_index,
                        )
                    )
                last_sent_at = now
                continue

            try:
                if args.no_post:
                    response = {}
                    state = "not_sent"
                else:
                    response = post_json("/sensor/mmwave", payload)
                    state = response.get("data", {}).get("status", {}).get("current_state")
                print(
                    f"{timestamp()} sent detected={detected} "
                    f"target=T{target_index if target_index is not None else 'none'} "
                    f"x={payload['x']} y={payload['y']} velocity={velocity:.2f} state={state}"
                )
                if args.debug_targets:
                    formatted = (
                        format_target(
                            index,
                            target,
                            roi,
                            space,
                            args.max_speed_cm_s,
                            slot_states,
                            now,
                            args.stale_seconds,
                            enforce_space,
                            selected_index=target_index,
                        )
                        for index, target in enumerate(targets, start=1)
                    )
                    print("  " + " | ".join(formatted))
                    print(
                        format_target_board(
                            targets,
                            roi,
                            space,
                            args.max_speed_cm_s,
                            slot_states,
                            now,
                            args.stale_seconds,
                            enforce_space,
                            target_index,
                        )
                    )
                last_sent_at = now
            except HTTPError as error:
                print(f"{timestamp()} HTTP error: {error.code} {error.reason}")
            except URLError as error:
                print(f"{timestamp()} Connection error: {error.reason}")


if __name__ == "__main__":
    main()
