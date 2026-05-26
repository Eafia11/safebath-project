import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import MODEL_PATH
from backend.app.ml.train import train_model, train_model_from_csv


DEFAULT_TRAINING_SAMPLES = [
    {"detected": True, "x": 1.8, "y": 1.5, "z": 1.35, "motion_level": 0.12, "still_time": 3, "zone": "toilet"},
    {"detected": True, "x": 2.0, "y": 1.4, "z": 1.36, "motion_level": 0.18, "still_time": 1, "zone": "toilet"},
    {"detected": True, "x": 1.0, "y": 0.8, "z": 1.42, "motion_level": 0.15, "still_time": 2, "zone": "sink"},
    {"detected": True, "x": 1.3, "y": 1.0, "z": 1.4, "motion_level": 0.2, "still_time": 0, "zone": "sink"},
    {"detected": True, "x": 1.5, "y": 1.1, "z": 1.2, "motion_level": 0.12, "still_time": 2, "zone": "bath"},
    {"detected": True, "x": 1.7, "y": 1.2, "z": 1.18, "motion_level": 0.1, "still_time": 4, "zone": "bath"},
    {"detected": False, "x": 0.0, "y": 0.0, "z": 0.0, "motion_level": 0.0, "still_time": 0},
]


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None
    metadata = train_model_from_csv(csv_path) if csv_path else train_model(DEFAULT_TRAINING_SAMPLES)
    print("Model retrained successfully.")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Metadata: {metadata}")


if __name__ == "__main__":
    main()
