import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BACKEND_URL = os.getenv("SAFEBATH_BACKEND_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("SAFEBATH_API_KEY", "")


def post_json(path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    request = Request(
        f"{BACKEND_URL}{path}",
        data=body,
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def send_mmwave_sample(
    *,
    detected: bool,
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    motion_level: float | None = None,
    velocity: float | None = None,
    still_time: int | None = None,
    zone: str | None = None,
) -> dict:
    payload = {
        "detected": detected,
        "x": x,
        "y": y,
        "z": z,
        "motion_level": motion_level,
        "velocity": velocity,
        "still_time": still_time,
        "zone": zone,
    }
    return post_json("/sensor/mmwave", payload)


def send_door_state(door_state: str) -> dict:
    return post_json("/sensor/door", {"door_state": door_state})


def send_button(button_type: str) -> dict:
    return post_json("/device/button", {"button_type": button_type})


def demo_loop():
    samples = [
        {"detected": True, "x": 0.2, "y": 0.4, "z": 1.2, "motion_level": 0.4, "velocity": 0.0, "still_time": 0},
        {"detected": True, "x": 0.3, "y": 0.5, "z": 1.1, "motion_level": 0.5, "velocity": 0.3, "still_time": 0},
        {"detected": True, "x": 0.4, "y": 0.5, "z": 1.1, "motion_level": 0.2, "velocity": 0.1, "still_time": 2},
    ]
    for sample in samples:
        response = send_mmwave_sample(**sample)
        status = response.get("data", {}).get("status", {})
        print(f"sent mmwave sample -> state={status.get('current_state')}")
        time.sleep(1)


if __name__ == "__main__":
    try:
        demo_loop()
    except HTTPError as error:
        print(f"HTTP error: {error.code} {error.reason}")
        print(error.read().decode("utf-8"))
    except URLError as error:
        print(f"Connection error: {error.reason}")
