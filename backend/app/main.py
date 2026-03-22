from fastapi import FastAPI
from app.core.config import HOST, PORT, DEBUG

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "SafeBath backend running",
        "host": HOST,
        "port": PORT,
        "debug": DEBUG
    }