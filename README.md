# SafeBath Project

SafeBath는 욕실 사용자의 안전 상태를 감지하기 위한 IoT 기반 욕실 안전 모니터링 시스템이다.
LD2450 mmWave 센서와 도어/버튼 입력을 백엔드로 전송하고, 백엔드는 상태 머신과 낙상/이상 감지
로직을 통해 현재 상태를 판단한다. 모바일 앱은 현재 욕실 상태와 존 보정 화면을 제공한다.

## 프로젝트 구성

- `backend/`: FastAPI 서버, 센서 처리, 상태 판단, 이상탐지, 저장소, 테스트
- `mobile/`: Android 모바일 앱
- `iot/`: Raspberry Pi 및 LD2450 센서 송신 스크립트
- `docs/`: 아키텍처, 파이프라인, API, 로그, 상태, 시연 문서
- `data/`: 로컬 실행 데이터, 로그, 캘리브레이션, 모델 파일 저장 위치
- `scripts/`: 더미 데이터 생성, 존 데이터 수집/분석, 모델 재학습 스크립트

## 백엔드 실행

프로젝트 루트에서 가상환경을 만들고 활성화한다.

```bash
python -m venv venv
venv\Scripts\activate
```

의존성을 설치한다.

```bash
pip install -r requirements.txt
```

백엔드를 실행한다.

```bash
uvicorn backend.app.main:app --reload
```

외부 장치에서 접근해야 할 때는 다음처럼 실행한다.

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

확인 주소:

```text
http://localhost:8000
http://localhost:8000/docs
```

상태 확인:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## 테스트

```bash
python -m pytest backend/tests
```

## 환경 변수

`.env.example`을 `.env`로 복사한 뒤 필요한 값을 수정한다.

```bash
copy .env.example .env
```

예시:

```env
HOST=127.0.0.1
PORT=8000
DEBUG=True
DATA_DIR=data
DATABASE_PATH=data/safebath.db
MODEL_PATH=backend/app/ml/saved_models/isolation_forest.pkl
API_KEY=
```

`API_KEY`를 설정하면 센서, 장치, 관리자 API 요청에 `x-api-key` 헤더가 필요하다.

## 모바일 앱

Android Studio에서 `mobile/` 디렉터리를 프로젝트로 연다.

백엔드 주소 기준:

- Android emulator: `http://10.0.2.2:8000/`
- 실제 기기: `http://<PC_IP>:8000/`

실제 기기에서 접근하려면 백엔드를 외부 접속 가능하게 실행한다.

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --reload
```

자세한 내용은 `mobile/README.md`를 참고한다.

## IoT 센서 연동

Raspberry Pi에서 LD2450 센서를 사용할 때는 IoT 의존성을 설치한다.

```bash
python3 -m venv iot-venv
source iot-venv/bin/activate
pip install -r iot/requirements.txt
```

백엔드 주소를 설정하고 송신 스크립트를 실행한다.

```bash
export SAFEBATH_BACKEND_URL=http://43.201.28.192:8000
export SAFEBATH_API_KEY=YOUR_API_KEY
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

자세한 내용은 `iot/README.md`를 참고한다.

## 존 캘리브레이션

현재 위치 존은 `toilet`, `sink`, `bath` 3개를 사용한다. 도어는 위치 존이 아니라 별도
도어 센서 이벤트(`/sensor/door`)로 처리한다.

존 데이터를 수집할 때는 PC 또는 AWS 백엔드를 실행한 뒤 Raspberry Pi sender를 켜고,
PC에서 다음 스크립트를 실행한다.

```bash
python scripts/collect_zone_data.py --backend-url http://43.201.28.192:8000 --labels empty toilet sink bath --duration 30
```

수집된 CSV는 `data/raw/zone_collection_YYYYMMDD_HHMMSS.csv`에 저장된다.

분석:

```bash
python scripts/analyze_zone_csv.py data/raw/zone_collection_YYYYMMDD_HHMMSS.csv --empty-noise-radius 0.15
```

## Docker 실행

Docker Compose로 백엔드를 실행할 수 있다.

```bash
docker compose up --build
```

백엔드는 `http://localhost:8000`에서 실행된다. Docker 실행 시 SQLite DB와 관련 데이터는
`safebath-data` 볼륨에 저장되어 컨테이너 재시작 이후에도 유지된다.

## 문서

문서는 `docs/README.md`에서 전체 목록과 추천 읽는 순서를 확인할 수 있다.

추천 순서:

- `docs/architecture.md`: 시스템 아키텍처와 모듈 역할
- `docs/pipeline.md`: 센서 입력부터 모바일 표시까지 전체 파이프라인
- `docs/demo-scenarios.md`: 발표 및 시연 시나리오
- `docs/setup-checklist.md`: 실행 및 발표 전 점검 목록
- `docs/zone-data-collection.md`: 60cm 모델 존 데이터 수집 절차
- `docs/api-spec.md`: 백엔드 API 명세
- `docs/state-spec.md`: 상태 머신 정의
- `docs/logging-spec.md`: 로그와 시계열 데이터 구조
- `docs/response-spec.md`: 공통 응답 형식

## 핵심 파이프라인

```text
LD2450 mmWave Sensor
  -> Raspberry Pi IoT Sender
  -> FastAPI Backend
  -> State Machine / Fall Detector / Anomaly Detector
  -> Repository / Logs / Alerts
  -> Android Mobile App
```

## AWS 배포 메모

현재 Dockerfile은 FastAPI 백엔드 이미지를 빌드하고 다음 명령으로 서버를 실행한다.

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

AWS에 배포할 경우 Amazon ECR에 이미지를 푸시한 뒤 ECS, Elastic Beanstalk Docker,
또는 EC2에서 실행할 수 있다. SQLite를 계속 사용한다면 `/app/data` 경로를 영구 스토리지에
연결해야 한다. 운영 환경에서 데이터 규모가 커지면 SQLite 대신 Amazon RDS/MySQL 또는
PostgreSQL 전환을 고려한다.
