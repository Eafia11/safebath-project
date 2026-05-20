CREATE_TABLE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        state TEXT NOT NULL DEFAULT 'ACTIVE',
        start_zone TEXT,
        last_zone TEXT,
        event_count INTEGER NOT NULL DEFAULT 0,
        duration_seconds REAL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sensor_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        sensor TEXT NOT NULL,
        session_id TEXT,
        detected INTEGER,
        x REAL,
        y REAL,
        z REAL,
        zone TEXT,
        motion_level REAL,
        velocity REAL,
        still_time INTEGER,
        door_state TEXT,
        payload_json TEXT NOT NULL,
        feature_json TEXT,
        anomaly_json TEXT,
        fall_detection_json TEXT,
        status_json TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS feature_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT 'mmwave',
        sensor_record_id INTEGER,
        session_id TEXT,
        detected REAL NOT NULL,
        motion_level REAL NOT NULL,
        still_time REAL NOT NULL,
        zone_score REAL NOT NULL,
        feature_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sensor_record_id) REFERENCES sensor_records(id),
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS anomaly_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        current_state TEXT,
        detected INTEGER NOT NULL,
        score REAL NOT NULL,
        threshold REAL NOT NULL,
        reason TEXT,
        prediction_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        type TEXT NOT NULL,
        level TEXT NOT NULL,
        target TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT NOT NULL,
        data_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS status_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_state TEXT NOT NULL,
        last_door_state TEXT,
        last_mmwave_detected INTEGER NOT NULL,
        last_zone TEXT,
        last_motion_level REAL,
        last_still_time INTEGER,
        last_reason TEXT NOT NULL,
        last_updated TEXT,
        waiting_for_response INTEGER NOT NULL,
        abnormal_start_time TEXT,
        last_fall_detected INTEGER NOT NULL DEFAULT 0,
        last_fall_score REAL NOT NULL DEFAULT 0,
        last_fall_at TEXT,
        snapshot_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS devices (
        device_name TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        last_seen_at TEXT,
        last_payload_json TEXT,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
]

CREATE_INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_sensor_records_sensor ON sensor_records(sensor)",
    "CREATE INDEX IF NOT EXISTS idx_sensor_records_timestamp ON sensor_records(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_sensor_records_session_id ON sensor_records(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_feature_records_timestamp ON feature_records(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_anomaly_predictions_timestamp ON anomaly_predictions(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_status_snapshots_created_at ON status_snapshots(created_at)",
]
