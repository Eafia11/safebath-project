# 실행 및 점검 체크리스트 (Setup Checklist)

이 문서는 발표 전 SafeBath 시스템을 점검하기 위한 체크리스트이다.

## 1. 백엔드

가상환경 생성:

```bash
python -m venv venv
venv\Scripts\activate
```

의존성 설치:

```bash
pip install -r requirements.txt
```

환경 변수:

```bash
copy .env.example .env
```

주요 값:

```env
HOST=127.0.0.1
PORT=8000
DEBUG=True
DATA_DIR=data
DATABASE_PATH=data/safebath.db
MODEL_PATH=backend/app/ml/saved_models/isolation_forest.pkl
API_KEY=
```

실행:

```bash
uvicorn backend.app.main:app --reload
```

확인:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## 2. 테스트

백엔드 테스트:

```bash
python -m pytest backend/tests
```

성공 기준:

```text
all tests passed
```

## 3. 모바일

Android Studio에서 `mobile/` 디렉터리를 연다.

확인할 것:

- JDK 또는 `JAVA_HOME` 설정
- Gradle sync 성공
- `BuildConfig.API_BASE_URL` 값 확인
- 에뮬레이터는 `http://10.0.2.2:8000/` 사용
- 실기기는 `http://<PC_IP>:8000/` 사용

명령어 빌드:

```bash
cd mobile
gradlew.bat test
```

## 4. IoT

Raspberry Pi 의존성 설치:

```bash
python3 -m venv iot-venv
source iot-venv/bin/activate
pip install -r iot/requirements.txt
```

백엔드 주소 설정:

```bash
export SAFEBATH_BACKEND_URL=http://YOUR_PC_IP:8000
export SAFEBATH_API_KEY=YOUR_API_KEY
```

센서 실행:

```bash
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

포트 확인:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

## 5. Docker

실행:

```bash
docker compose up --build
```

확인:

```bash
curl http://localhost:8000/health
```

## 6. 발표 전 최종 점검

| 항목 | 확인 |
| --- | --- |
| 백엔드 실행 가능 |  |
| `/health` 정상 응답 |  |
| `/status` 정상 응답 |  |
| 백엔드 테스트 통과 |  |
| 모바일 앱 실행 가능 |  |
| 모바일에서 서버 연결 성공 |  |
| 캘리브레이션 시나리오 성공 |  |
| mmWave 센서 전송 성공 |  |
| 이상상황 시나리오 성공 |  |
| 알림 조회 성공 |  |
| `/admin/tuning.csv` 다운로드 가능 |  |
| README와 문서 최신화 |  |

## 7. 문제 해결

### 모바일 Gradle 실행 시 Java 오류

증상:

```text
JAVA_HOME is not set and no 'java' command could be found in your PATH.
```

해결:

- JDK 설치
- `JAVA_HOME` 환경 변수 설정
- 새 터미널에서 `java -version` 확인

### Raspberry Pi에서 서버 연결 실패

확인:

- 백엔드를 `--host 0.0.0.0`으로 실행했는지 확인
- PC와 Raspberry Pi가 같은 네트워크에 있는지 확인
- `SAFEBATH_BACKEND_URL`이 `localhost`가 아니라 PC IP인지 확인
- Windows 방화벽에서 8000 포트를 허용했는지 확인

### 센서 좌표가 튀는 경우

확인:

- `--debug-targets`로 모든 target 확인
- ROI 범위 조정
- `--roi-y-min`, `--roi-y-max`, `--roi-x-limit` 값 조정
- `--stale-seconds`로 정지 target 필터링 조정
