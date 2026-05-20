import json
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_dir(path: str | Path) -> Path:
    file_path = Path(path)
    if file_path.parent:
        ensure_dir(file_path.parent)
    return file_path


def read_json(path: str | Path, default: Any = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str | Path, data: Any):
    file_path = ensure_parent_dir(path)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
