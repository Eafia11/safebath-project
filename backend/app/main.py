from fastapi import FastAPI
from app.core.config import HOST, PORT, DEBUG
from app.api import health, status, sensor, device, logs, alerts, calibration

app = FastAPI()

app.include_router(health.router)
app.include_router(status.router)
app.include_router(sensor.router)
app.include_router(device.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(calibration.router)

@app.get("/")
def root():
    return {
        "message": "SafeBath backend running",
        "host": HOST,
        "port": PORT,
        "debug": DEBUG
    }