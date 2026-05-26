# 시스템 아키텍처 (Architecture)

SafeBath는 욕실 내 사용자의 안전 상태를 감지하고 보호자에게 위험 상황을 알리기 위한
IoT 기반 모니터링 시스템이다.

## 구성 요소

| 영역 | 역할 | 주요 위치 |
| --- | --- | --- |
| IoT 센서 | LD2450 mmWave 센서 데이터 수집 및 백엔드 전송 | `iot/` |
| 백엔드 API | 센서 수신, 상태 판단, 이상탐지, 로그/세션/알림 관리 | `backend/app/` |
| 모바일 앱 | 사용자/보호자 화면, 상태 확인, 캘리브레이션 | `mobile/` |
| 데이터 저장 | 센서 기록, feature, 세션, 상태, 알림 저장 | `backend/app/repositories/`, `data/` |
| 문서 | API, 상태, 로그, 시연 절차 정리 | `docs/` |

## 전체 구조

```text
LD2450 mmWave Sensor
        |
        v
Raspberry Pi / IoT Script
        |
        | POST /sensor/mmwave
        v
FastAPI Backend
        |
        +--> Zone Resolution
        +--> Feature Pipeline
        +--> Rule-based State Machine
        +--> Fall Detector
        +--> Anomaly Detector
        +--> Session / Log / Alert Repository
        |
        | GET /status, /alerts, /calibration
        v
Android Mobile App
```

## 백엔드 내부 흐름

```text
API Router
  -> Service
    -> Detector / ML / State Machine
    -> Repository
  -> CommonResponse
```

주요 계층:

- `api`: HTTP 엔드포인트 정의
- `services`: 비즈니스 로직 처리
- `detectors`: 낙상, 비활동, fusion 판단
- `ml`: feature 변환, IsolationForest 학습/예측
- `repositories`: 런타임 데이터 저장
- `models`: 요청/응답/도메인 모델

## 주요 판단 로직

상태 판단:

- 도어 이벤트와 mmWave 감지 여부로 `EMPTY`, `ENTERING`, `ACTIVE`를 판단한다.
- 좌표 또는 명시적 zone 정보로 `TOILET_USE`를 판단한다.
- 장시간 정지 또는 낙상 의심 시 `ABNORMAL`로 전환한다.
- 사용자 응답이 없으면 `EMERGENCY`로 전환하고 알림을 생성한다.

이상탐지:

- mmWave 입력을 feature vector로 변환한다.
- IsolationForest 모델이 학습되어 있으면 모델 점수와 예측을 사용한다.
- 모델이 없으면 heuristic score를 fallback으로 사용한다.

낙상탐지:

- 이전 샘플과 현재 샘플의 높이 변화, 속도 변화, 정지 시간을 비교한다.
- 조건이 충족되면 사용자 응답 대기 상태로 전환한다.

## 모바일 앱 역할

모바일 앱은 현재 상태를 사용자에게 보여주고, 초기 설치 시 존 보정을 수행한다.

현재 연결 API:

- `GET /health`
- `GET /status`
- `POST /calibration/start`
- `POST /calibration/step`
- `POST /calibration/complete`

화면 구성:

- 로그인/모드 선택
- 존 캘리브레이션
- 실시간 상태 대시보드
- 리포트
- 설정/초기화

## IoT 역할

`iot/ld2450_sender.py`는 LD2450 UART 프레임을 읽고 다음 처리를 수행한다.

- 3개 target 슬롯 파싱
- ROI 필터링
- stale target 제거
- 대표 target 선택
- 좌표, 속도, 정지 시간 계산
- `POST /sensor/mmwave` 전송

## 배포 구조

로컬 개발:

```text
uvicorn backend.app.main:app --reload
```

Docker:

```text
docker compose up --build
```

운영 확장 시 고려사항:

- SQLite 대신 PostgreSQL/MySQL 전환
- 로그 영구 저장
- API key 관리
- HTTPS 적용
- 장치 heartbeat 모니터링
