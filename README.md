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

Run with Docker Compose:

```bash
docker compose up --build
```

The backend will be available at `http://localhost:8000`. Runtime data is stored in the `safebath-data` Docker volume so the SQLite database and logs survive container restarts.

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

## Docker and AWS Deployment Notes

The included `Dockerfile` builds the FastAPI backend image and runs:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

For AWS, build and push this image to a registry such as Amazon ECR, then run it on ECS, Elastic Beanstalk Docker, or an EC2 instance. Keep `/app/data` on persistent storage if you continue using SQLite in production. If the project later moves to Amazon RDS/MySQL, replace the SQLite file settings with database connection environment variables and remove the local data volume dependency.
