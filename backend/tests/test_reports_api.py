from datetime import datetime, timedelta

from app.repositories.sensor_repository import sensor_repository


def test_weekly_report_aggregates_raw_mmwave_records(client):
    first = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.53,
            "y": 1.36,
            "z": 1.2,
            "motion_level": 0.08,
            "velocity": 0.1,
            "still_time": 240,
            "zone": "toilet",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.53,
            "y": 1.36,
            "z": 0.5,
            "motion_level": 0.0,
            "velocity": 1.2,
            "still_time": 900,
            "zone": "toilet",
        },
    )
    assert second.status_code == 200

    records = sensor_repository.list_records(sensor="mmwave")
    records[0]["timestamp"] = (datetime.utcnow() - timedelta(days=1)).replace(
        hour=23,
        minute=10,
        second=0,
        microsecond=0,
    ).isoformat()
    records[1]["timestamp"] = (datetime.utcnow() - timedelta(days=1)).replace(
        hour=12,
        minute=0,
        second=0,
        microsecond=0,
    ).isoformat()

    response = client.get("/reports/weekly")

    assert response.status_code == 200
    data = response.json()["data"]
    summary = data["summary"]
    assert data["source"] == "raw_mmwave_records"
    assert data["preprocessing"]["bucket_seconds"] == 60
    assert summary["raw_record_count"] == 2
    assert summary["processed_record_count"] == 2
    assert summary["detected_count"] == 2
    assert summary["fall_count"] == 1
    assert summary["anomaly_count"] >= 1
    assert summary["night_toilet_count"] == 1
    assert summary["zone_duration_seconds"]["toilet"] == 120
    assert len(data["daily"]) == 7
    assert any(event["type"] == "fall" for event in data["abnormal_events"])


def test_weekly_report_preprocesses_dense_raw_mmwave_records(client):
    for second in (0, 10, 20):
        response = client.post(
            "/sensor/mmwave",
            json={
                "detected": True,
                "x": 0.53,
                "y": 1.36,
                "z": 1.2,
                "motion_level": 0.08,
                "velocity": 0.1,
                "still_time": second + 1,
                "zone": "toilet",
            },
        )
        assert response.status_code == 200

    records = sensor_repository.list_records(sensor="mmwave")
    base = (datetime.utcnow() - timedelta(days=1)).replace(
        hour=23,
        minute=10,
        second=0,
        microsecond=0,
    )
    for index, record in enumerate(records):
        record["timestamp"] = (base + timedelta(seconds=index * 10)).isoformat()

    response = client.get("/reports/weekly")

    assert response.status_code == 200
    summary = response.json()["data"]["summary"]
    assert summary["raw_record_count"] == 3
    assert summary["processed_record_count"] == 1
    assert summary["detected_count"] == 1
    assert summary["night_toilet_count"] == 1
    assert summary["zone_duration_seconds"]["toilet"] == 60
