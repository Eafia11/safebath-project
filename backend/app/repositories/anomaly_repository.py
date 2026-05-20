from typing import List, Optional

from ..models.anomaly import AnomalyPrediction


class AnomalyRepository:
    def __init__(self):
        self.predictions: List[AnomalyPrediction] = []

    def save(self, prediction: AnomalyPrediction) -> AnomalyPrediction:
        stored_prediction = prediction.model_copy()
        self.predictions.append(stored_prediction)
        return stored_prediction

    def list_predictions(self) -> List[AnomalyPrediction]:
        return self.predictions

    def get_latest(self) -> Optional[AnomalyPrediction]:
        if not self.predictions:
            return None
        return self.predictions[-1]

    def clear(self):
        self.predictions.clear()


anomaly_repository = AnomalyRepository()
