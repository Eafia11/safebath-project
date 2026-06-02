from fastapi import FastAPI

from .api import admin, alerts, anomalies, calibration, device, health, logs, reports, sensor, sessions, status
from .core.config import DEBUG, HOST, PORT
from .db.init_db import init_db


init_db()


app = FastAPI(
    title="SafeBath Backend",
    version="0.1.0",
)

for router in (
    health.router,
    status.router,
    sensor.router,
    device.router,
    logs.router,
    alerts.router,
    calibration.router,
    anomalies.router,
    sessions.router,
    reports.router,
    admin.router,
):
    app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "SafeBath backend running",
        "host": HOST,
        "port": PORT,
        "debug": DEBUG,
        "registered_routers": [
            "health",
            "status",
            "sensor",
            "device",
            "logs",
            "alerts",
            "calibration",
            "anomalies",
            "sessions",
            "reports",
            "admin",
        ],
    }
