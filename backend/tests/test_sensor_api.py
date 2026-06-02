from datetime import datetime, timedelta

from app.repositories.sensor_repository import sensor_repository
from app.services.state_service import state_service


def test_receive_mmwave_saves_raw_coordinates(client):
    response = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 1.2,
            "y": 2.3,
            "motion_level": 0.1,
            "still_time": 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert body["success"] is True
    assert data["payload"]["x"] == 1.2
    assert data["payload"]["y"] == 2.3
    assert data["feature_vector"]["detected"] == 1.0
    assert data["fusion_detection"]["level"] == "normal"

    latest_record = sensor_repository.get_latest("mmwave")
    assert latest_record["x"] == 1.2
    assert latest_record["y"] == 2.3


def test_receive_door_event_updates_status(client):
    response = client.post("/sensor/door", json={"door_state": "open"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["payload"]["door_state"] == "open"
    assert data["status"]["current_state"] == "ENTERING"


def test_closed_door_uses_latest_mmwave_presence(client):
    client.post("/sensor/door", json={"door_state": "open"})
    client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.5,
            "y": 1.3,
            "motion_level": 0.1,
            "still_time": 0,
        },
    )

    active_response = client.post("/sensor/door", json={"door_state": "closed"})

    assert active_response.status_code == 200
    active_status = active_response.json()["data"]["status"]
    assert active_status["current_state"] == "ACTIVE"

    client.post(
        "/sensor/mmwave",
        json={
            "detected": False,
            "x": None,
            "y": None,
            "motion_level": 0.0,
            "still_time": 0,
        },
    )

    empty_response = client.post("/sensor/door", json={"door_state": "closed"})

    assert empty_response.status_code == 200
    empty_status = empty_response.json()["data"]["status"]
    assert empty_status["current_state"] == "EMPTY"


def test_receive_mmwave_triggers_speaker_when_possible_fall_detected(client):
    first_response = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.0,
            "y": 0.0,
            "z": 1.2,
            "motion_level": 0.5,
            "velocity": 0.0,
            "still_time": 0,
        },
    )
    assert first_response.status_code == 200

    fall_response = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.1,
            "y": 0.1,
            "z": 0.7,
            "motion_level": 0.0,
            "velocity": 1.0,
            "still_time": 10,
        },
    )

    assert fall_response.status_code == 200
    data = fall_response.json()["data"]
    assert data["fall_detection"]["candidate_detected"] is True
    assert data["fall_detection"]["detected"] is False
    assert data["status"]["current_state"] == "ABNORMAL"
    assert data["status"]["waiting_for_response"] is True
    assert data["status"]["pending_response_type"] == "fall"
    assert data["status"]["last_fall_detected"] is False
    assert data["speaker_request"]["requested"] is True
    assert data["speaker_request"]["payload"]["alert_level"] == "danger"
    assert "낙상이 감지되었습니다" in data["speaker_request"]["payload"]["message"]


def test_possible_fall_becomes_emergency_when_button_is_not_pressed(client):
    client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.0,
            "y": 0.0,
            "z": 1.2,
            "motion_level": 0.5,
            "velocity": 0.0,
            "still_time": 0,
        },
    )
    client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.1,
            "y": 0.1,
            "z": 0.7,
            "motion_level": 0.0,
            "velocity": 1.0,
            "still_time": 10,
        },
    )

    state_service.abnormal_start_time = datetime.utcnow() - timedelta(seconds=61)
    timeout_response = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.1,
            "y": 0.1,
            "z": 0.7,
            "motion_level": 0.0,
            "velocity": 0.0,
            "still_time": 11,
        },
    )

    assert timeout_response.status_code == 200
    data = timeout_response.json()["data"]
    assert data["status"]["current_state"] == "EMERGENCY"
    assert data["status"]["waiting_for_response"] is False
    assert data["status"]["pending_response_type"] is None
    assert data["status"]["last_reason"] == "No user response after possible fall"
    assert data["status"]["last_emergency_source"] == "fall"
    assert data["status"]["last_fall_detected"] is True
    assert data["fall_detection"]["detected"] is True
