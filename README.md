# SafeBath Project

IoT-based bathroom safety monitoring system for a capstone project.

## Structure

- `backend/`: FastAPI server, sensor processing, detectors, repositories, and tests
- `mobile/`: Android mobile app
- `iot/`: IoT sensor examples and device-side code
- `docs/`: API, logging, response, and state documentation
- `data/`: Local runtime data folders

## Backend Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

Run the backend from the project root:

```bash
uvicorn backend.app.main:app --reload
```

Run tests from the project root:

```bash
python -m pytest backend/tests
```

## Environment

Copy `.env.example` to `.env` and edit values as needed.

```env
HOST=127.0.0.1
PORT=8000
DEBUG=True
DATA_DIR=data
DATABASE_PATH=data/safebath.db
MODEL_PATH=backend/app/ml/saved_models/isolation_forest.pkl
API_KEY=
```
