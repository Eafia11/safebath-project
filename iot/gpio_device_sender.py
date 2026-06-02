import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from gpiozero import Button, DigitalOutputDevice
except ImportError:  # pragma: no cover - only hit on non-Pi/dev machines.
    Button = None
    DigitalOutputDevice = None


BACKEND_URL = os.getenv("SAFEBATH_BACKEND_URL", "http://43.201.28.192:8000")
API_KEY = os.getenv("SAFEBATH_API_KEY", "")

DEFAULT_DOOR_PIN = int(os.getenv("SAFEBATH_DOOR_PIN", "17"))
DEFAULT_BUTTON_PIN = int(os.getenv("SAFEBATH_BUTTON_PIN", "27"))
DEFAULT_SPEAKER_PIN = int(os.getenv("SAFEBATH_SPEAKER_PIN", "18"))
DEFAULT_FALL_AUDIO_FILE = os.getenv(
    "SAFEBATH_FALL_AUDIO_FILE",
    str(Path(__file__).resolve().parent / "audio" / "fall_warning.mp3"),
)
DEFAULT_FALL_TTS_TEXT = os.getenv(
    "SAFEBATH_FALL_TTS_TEXT",
    "낙상이 감지되었습니다. 괜찮으시면 버튼을 눌러주세요.",
)


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def request_json(path: str, payload: dict | None = None, method: str = "GET") -> dict:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(f"{BACKEND_URL}{path}", data=body, headers=headers, method=method)
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(path: str, payload: dict) -> dict:
    return request_json(path, payload=payload, method="POST")


def get_status() -> dict:
    response = request_json("/status")
    return response.get("data", {})


def send_door_state(door_state: str) -> None:
    response = post_json("/sensor/door", {"door_state": door_state})
    status = response.get("data", {}).get("status", {})
    print(f"{timestamp()} sent door={door_state} state={status.get('current_state')}")


def send_button(button_type: str) -> None:
    response = post_json("/device/button", {"button_type": button_type})
    status = response.get("data", {}).get("status", {})
    print(f"{timestamp()} sent button={button_type} state={status.get('current_state')}")


class Buzzer:
    def __init__(self, pin: int | None, enabled: bool) -> None:
        self.enabled = enabled and pin is not None
        self.output = None
        self._lock = threading.Lock()
        if self.enabled:
            self.output = DigitalOutputDevice(pin, active_high=True, initial_value=False)

    def close(self) -> None:
        if self.output:
            self.output.off()
            self.output.close()

    def beep(self, count: int, on_seconds: float, off_seconds: float) -> None:
        if not self.output:
            return
        with self._lock:
            for _ in range(count):
                self.output.on()
                time.sleep(on_seconds)
                self.output.off()
                time.sleep(off_seconds)

    def warning(self) -> None:
        self.beep(count=2, on_seconds=0.15, off_seconds=0.12)

    def danger(self) -> None:
        self.beep(count=5, on_seconds=0.12, off_seconds=0.08)


class AudioPlayer:
    def __init__(
        self,
        audio_file: str | None,
        enabled: bool,
        tts_text: str | None,
        audio_backend: str,
        regenerate_tts: bool,
    ) -> None:
        self.audio_file = Path(audio_file).expanduser() if audio_file else None
        self.enabled = enabled and self.audio_file is not None
        self.tts_text = tts_text
        self.audio_backend = audio_backend
        self.regenerate_tts = regenerate_tts
        self._lock = threading.Lock()

    def play(self) -> None:
        if not self.enabled or self.audio_file is None:
            return
        if not self._ensure_audio_file():
            return

        if self.audio_backend in {"auto", "pygame"} and self._play_with_pygame():
            return

        if self.audio_backend == "pygame":
            return

        command = self._build_command()
        if command is None:
            print(f"{timestamp()} no audio player found. Install pygame or ffmpeg.")
            return
        threading.Thread(target=self._run, args=(command,), daemon=True).start()

    def _ensure_audio_file(self) -> bool:
        if self.audio_file is None:
            return False
        if self.audio_file.exists() and not self.regenerate_tts:
            return True
        if not self.tts_text:
            print(f"{timestamp()} audio file not found: {self.audio_file}")
            return False

        try:
            from gtts import gTTS
        except ImportError:
            print(f"{timestamp()} gTTS is not installed. Run: pip install -r iot/requirements.txt")
            return False

        self.audio_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            gTTS(text=self.tts_text, lang="ko").save(str(self.audio_file))
        except Exception as error:
            print(f"{timestamp()} gTTS generation failed: {error}")
            return False
        print(f"{timestamp()} generated fall audio: {self.audio_file}")
        return True

    def _play_with_pygame(self) -> bool:
        try:
            import pygame
        except ImportError:
            if self.audio_backend == "pygame":
                print(f"{timestamp()} pygame is not installed. Run: pip install -r iot/requirements.txt")
            return False

        def run() -> None:
            with self._lock:
                try:
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(self.audio_file))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except Exception as error:
                    print(f"{timestamp()} pygame playback error: {error}")
                finally:
                    try:
                        pygame.mixer.quit()
                    except Exception:
                        pass

        threading.Thread(target=run, daemon=True).start()
        return True

    def _build_command(self) -> list[str] | None:
        path = str(self.audio_file)
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-hide_banner", "-loglevel", "error", path]
        if shutil.which("cvlc"):
            return ["cvlc", "--play-and-exit", "--quiet", path]
        if self.audio_file.suffix.lower() == ".wav" and shutil.which("aplay"):
            return ["aplay", path]
        if self.audio_file.suffix.lower() in {".mp3", ".mp2"} and shutil.which("mpg123"):
            return ["mpg123", "-q", path]
        return None

    def _run(self, command: list[str]) -> None:
        with self._lock:
            try:
                subprocess.run(command, check=False)
            except OSError as error:
                print(f"{timestamp()} audio playback error: {error}")


class DeviceHub:
    def __init__(self, args: argparse.Namespace) -> None:
        if Button is None or DigitalOutputDevice is None:
            raise SystemExit("gpiozero is not installed. Run: pip install -r iot/requirements.txt")

        self.args = args
        self.stop_event = threading.Event()
        self.door_closed_when_pressed = args.door_closed_when_pressed
        self.last_door_state: str | None = None
        self.last_speaker_state: str | None = None
        self.last_fall_audio_key: str | None = None
        self.latest_status: dict = {}
        self.buzzer = Buzzer(args.speaker_pin, not args.no_speaker)
        self.audio_player = AudioPlayer(
            args.fall_audio_file,
            not args.no_audio,
            args.fall_tts_text,
            args.audio_backend,
            args.regenerate_tts,
        )
        self.devices = []

    def setup(self) -> None:
        self.door = Button(
            self.args.door_pin,
            pull_up=self.args.pull_up,
            bounce_time=self.args.bounce_seconds,
        )
        self.door.when_pressed = self.handle_door_changed
        self.door.when_released = self.handle_door_changed
        self.devices.append(self.door)

        self._setup_button(self.args.button_pin)

        self.handle_door_changed(initial=True)

    def _setup_button(self, pin: int | None) -> None:
        if pin is None:
            return
        button = Button(pin, pull_up=self.args.pull_up, bounce_time=self.args.bounce_seconds)
        button.when_pressed = self.handle_button_pressed
        self.devices.append(button)

    def close(self) -> None:
        self.stop_event.set()
        for device in self.devices:
            device.close()
        self.buzzer.close()

    def handle_door_changed(self, initial: bool = False) -> None:
        pressed = self.door.is_pressed
        door_state = "closed" if pressed == self.door_closed_when_pressed else "open"
        if door_state == self.last_door_state:
            return
        self.last_door_state = door_state

        if initial and self.args.skip_initial_door_event:
            print(f"{timestamp()} initial door={door_state} skipped")
            return
        self._safe_call(send_door_state, door_state)

    def resolve_button_type(self) -> str:
        if self.args.button_mode != "smart":
            return self.args.button_mode

        status = self.latest_status
        current_state = status.get("current_state")
        pending = status.get("pending_response_type")
        if current_state == "ABNORMAL" or pending:
            return "confirm_safe"
        return "emergency_call"

    def handle_button_pressed(self) -> None:
        button_type = self.resolve_button_type()
        self._safe_call(send_button, button_type)
        if button_type == "emergency_call":
            self.buzzer.danger()
        elif button_type in {"confirm_safe", "reset"}:
            self.buzzer.warning()

    def poll_status_for_speaker(self) -> None:
        while not self.stop_event.wait(self.args.status_interval):
            try:
                status = get_status()
            except (HTTPError, URLError, TimeoutError) as error:
                print(f"{timestamp()} status poll error: {error}")
                continue

            self.latest_status = status
            current_state = status.get("current_state")
            pending = status.get("pending_response_type")
            fall_audio_key = (
                status.get("abnormal_start_time")
                or status.get("last_fall_at")
                or "fall"
            )
            if pending == "fall" and fall_audio_key != self.last_fall_audio_key:
                self.last_fall_audio_key = fall_audio_key
                print(f"{timestamp()} playing fall audio: {self.audio_player.audio_file}")
                self.audio_player.play()

            speaker_state = f"{current_state}:{pending}"
            if speaker_state == self.last_speaker_state:
                continue
            self.last_speaker_state = speaker_state

            if current_state == "EMERGENCY":
                print(f"{timestamp()} speaker danger for state=EMERGENCY")
                self.buzzer.danger()
            elif current_state == "ABNORMAL" or pending:
                print(f"{timestamp()} speaker warning for state={current_state} pending={pending}")
                self.buzzer.warning()

    def run(self) -> None:
        self.setup()
        if not self.args.no_status_poll:
            threading.Thread(target=self.poll_status_for_speaker, daemon=True).start()

        print(f"{timestamp()} GPIO device sender started")
        print(
            "Pins: "
            f"door={self.args.door_pin}, button={self.args.button_pin}({self.args.button_mode}), "
            f"speaker={self.args.speaker_pin if not self.args.no_speaker else 'off'}"
        )
        while not self.stop_event.wait(1):
            pass

    def _safe_call(self, callback, *args) -> None:
        try:
            callback(*args)
        except HTTPError as error:
            print(f"{timestamp()} HTTP error: {error.code} {error.reason}")
            print(error.read().decode("utf-8"))
        except (URLError, TimeoutError) as error:
            print(f"{timestamp()} Connection error: {error}")


def parse_optional_pin(value: str) -> int | None:
    if value.lower() in {"none", "off", "disabled"}:
        return None
    return int(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read Raspberry Pi GPIO door/button inputs and drive a buzzer for SafeBath.",
    )
    parser.add_argument("--door-pin", type=int, default=DEFAULT_DOOR_PIN)
    parser.add_argument("--button-pin", type=parse_optional_pin, default=DEFAULT_BUTTON_PIN)
    parser.add_argument(
        "--button-mode",
        choices=["smart", "confirm_safe", "emergency_call", "reset"],
        default=os.getenv("SAFEBATH_BUTTON_MODE", "smart"),
        help="smart: confirm_safe during pending response, emergency_call otherwise.",
    )
    parser.add_argument("--speaker-pin", type=parse_optional_pin, default=DEFAULT_SPEAKER_PIN)
    parser.add_argument("--pull-up", action=argparse.BooleanOptionalAction, default=bool_env("SAFEBATH_GPIO_PULL_UP", True))
    parser.add_argument("--door-closed-when-pressed", action=argparse.BooleanOptionalAction, default=bool_env("SAFEBATH_DOOR_CLOSED_WHEN_PRESSED", True))
    parser.add_argument("--bounce-seconds", type=float, default=float(os.getenv("SAFEBATH_GPIO_BOUNCE_SECONDS", "0.08")))
    parser.add_argument("--status-interval", type=float, default=float(os.getenv("SAFEBATH_STATUS_POLL_SECONDS", "2.0")))
    parser.add_argument("--skip-initial-door-event", action="store_true")
    parser.add_argument("--no-speaker", action="store_true")
    parser.add_argument("--fall-audio-file", default=DEFAULT_FALL_AUDIO_FILE)
    parser.add_argument("--fall-tts-text", default=DEFAULT_FALL_TTS_TEXT)
    parser.add_argument("--audio-backend", choices=["auto", "pygame", "command"], default=os.getenv("SAFEBATH_AUDIO_BACKEND", "auto"))
    parser.add_argument("--regenerate-tts", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--no-status-poll", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    hub = DeviceHub(args)

    def stop(_signum, _frame) -> None:
        hub.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        hub.run()
    finally:
        hub.close()


if __name__ == "__main__":
    main()
