from datetime import datetime, timedelta

from app.services.state_service import state_service


def test_get_status_returns_initial_state(client):
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["current_state"] == "EMPTY"
    assert data["last_mmwave_detected"] is False
    assert data["active_session"] is None


def test_get_status_after_mmwave_event(client):
    client.post("/sensor/mmwave", json={"detected": True, "x": 0.1, "y": 0.2})
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["current_state"] == "ACTIVE"
    assert data["last_mmwave_detected"] is True
    assert data["active_session"] is not None


def test_get_status_marks_active_empty_when_mmwave_is_stale(client):
    client.post("/sensor/mmwave", json={"detected": True, "x": 0.1, "y": 0.2})
    state_service.last_mmwave_seen_at = datetime.utcnow() - timedelta(seconds=11)

    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["current_state"] == "EMPTY"
    assert data["last_mmwave_detected"] is False
