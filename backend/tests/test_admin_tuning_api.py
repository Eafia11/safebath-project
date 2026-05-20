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
