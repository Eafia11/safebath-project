from datetime import datetime, timedelta


def test_admin_tuning_records_include_fall_and_anomaly_fields(client):
    client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 1.0,
            "y": 2.0,
            "z": 1.1,
            "motion_level": 0.3,
            "velocity": 0.2,
            "still_time": 4,
            "zone": "sink",
        },
    )

    response = client.get("/admin/tuning")

    assert response.status_code == 200
    records = response.json()["data"]["records"]
    assert len(records) == 1
    assert records[0]["x"] == 1.0
    assert records[0]["zone"] == "sink"
    assert "fall_score" in records[0]
    assert "anomaly_score" in records[0]
    assert "current_state" in records[0]


def test_admin_tuning_csv_download(client):
    client.post(
        "/sensor/mmwave",
        json={
            "detected": True,
            "x": 0.5,
            "y": 0.6,
            "z": 1.0,
            "motion_level": 0.2,
            "still_time": 1,
        },
    )

    response = client.get("/admin/tuning.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "height_drop" in response.text
    assert "anomaly_score" in response.text


def test_admin_demo_mmwave_import_feeds_weekly_report(client):
    base = (datetime.utcnow() - timedelta(days=1)).replace(
        hour=8,
        minute=0,
        second=0,
        microsecond=0,
    )
    response = client.post(
        "/admin/demo/mmwave",
        json={
            "clear_existing": True,
            "records": [
                {
                    "timestamp": base.isoformat(),
                    "detected": True,
                    "x": 0.12,
                    "y": 0.68,
                    "z": 1.08,
                    "zone": "toilet",
                    "motion_level": 0.08,
                    "velocity": 0.1,
                    "still_time": 180,
                    "current_state": "TOILET_USE",
                },
                {
                    "timestamp": (base + timedelta(minutes=10)).isoformat(),
                    "detected": True,
                    "x": -0.24,
                    "y": 0.72,
                    "z": 0.42,
                    "zone": "bath",
                    "motion_level": 0.01,
                    "velocity": 1.2,
                    "still_time": 60,
                    "current_state": "EMERGENCY",
                    "anomaly_detected": True,
                    "anomaly_score": 0.94,
                    "anomaly_reason": "fall candidate remained unresolved",
                    "fall_detected": True,
                    "fall_score": 0.96,
                    "fall_reason": "low height with high velocity in bath zone",
                    "emergency_source": "fall",
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["imported_count"] == 2

    report = client.get("/reports/weekly?days=31")

    assert report.status_code == 200
    summary = report.json()["data"]["summary"]
    assert summary["raw_record_count"] == 2
    assert summary["fall_count"] == 1
    assert summary["emergency_by_source"]["fall"] == 1
