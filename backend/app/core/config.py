import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
API_KEY = os.getenv("API_KEY")


def _rooted_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str(ROOT_DIR / path)


DATA_DIR = _rooted_path(os.getenv("DATA_DIR", "data"))
DATABASE_PATH = _rooted_path(os.getenv("DATABASE_PATH", os.path.join("data", "safebath.db")))
MODEL_PATH = _rooted_path(
    os.getenv(
        "MODEL_PATH",
        os.path.join("backend", "app", "ml", "saved_models", "isolation_forest.pkl"),
    )
)
