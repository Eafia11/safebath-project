import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.pop("API_KEY", None)
os.environ.setdefault("DATABASE_PATH", "data/test_safebath.db")

from app.main import app


@pytest.fixture(autouse=True)
def reset_app_state():
    from app.detectors.fall_detector import fall_detector
    from app.repositories.alert_repository import alert_repository
    from app.repositories.anomaly_repository import anomaly_repository
    from app.repositories.feature_repository import feature_repository
    from app.repositories.sensor_repository import sensor_repository
    from app.repositories.session_repository import session_repository
    from app.repositories.status_repository import status_repository
    from app.services.alert_service import alert_service
    from app.services.anomaly_service import anomaly_service
    from app.services.log_service import log_service
    from app.services.model_service import model_service
    from app.services.session_service import session_service
    from app.services.state_service import state_service

    state_service.current_state = "EMPTY"
    state_service.last_door_state = None
    state_service.last_mmwave_detected = False
    state_service.last_zone = None
    state_service.last_motion_level = None
    state_service.last_still_time = None
    state_service.last_reason = "Initial state"
    state_service.last_updated = None
    state_service.abnormal_start_time = None
    state_service.waiting_for_response = False
    state_service.pending_response_type = None
    state_service.last_fall_detected = False
    state_service.last_fall_score = 0.0
    state_service.last_fall_at = None
    state_service.pending_fall_reason = None

    session_service.sessions.clear()
    session_service.active_session_id = None
    alert_service.alerts.clear()
    log_service.logs.clear()
    anomaly_service.latest_prediction = None
    fall_detector.last_sample = None
    model_service.sample_count = 0
    model_service.average_motion_level = 0.0
    model_service.last_trained_at = None
    model_service.isolation_forest.model = None
    model_service.isolation_forest.sample_count = 0

    alert_repository.clear()
    anomaly_repository.clear()
    feature_repository.clear()
    sensor_repository.clear()
    session_repository.clear()
    status_repository.clear()

    yield


@pytest.fixture
def client():
    return TestClient(app)
