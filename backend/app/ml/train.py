from typing import Iterable

from .preprocess import build_training_samples, load_training_samples_from_csv
from ..services.model_service import model_service


def train_model(raw_samples: Iterable[dict]):
    samples = build_training_samples(raw_samples)
    return model_service.train(samples)


def train_model_from_csv(csv_path: str):
    samples = load_training_samples_from_csv(csv_path)
    return model_service.train(samples)
