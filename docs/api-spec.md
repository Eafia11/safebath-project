# API 명세 (API Specification)

SafeBath 백엔드는 FastAPI 기반 HTTP API를 제공한다. 모든 일반 API는 공통 응답 형식
`success`, `message`, `data`를 사용한다.

기본 주소:

```text
http://localhost:8000
```

Swagger 문서:

```text
http://localhost:8000/docs
```

## 인증

다음 API는 `.env`의 `API_KEY`가 설정된 경우 `x-api-key` 헤더가 필요하다.

- `POST /sensor/mmwave`
- `POST /sensor/door`
- `POST /device/button`
- `POST /device/speaker`
- `POST /device/heartbeat`
- `GET /device/status`
- `GET /admin/snapshot`
- `GET /admin/tuning`
- `GET /admin/tuning.csv`

예시:

```http
x-api-key: your-api-key
```

## 공통 응답

```json
{
  "success": true,
  "message": "Current status retrieved successfully.",
  "data": {}
}
```

## Health

### GET /health

서버가 정상적으로 실행 중인지 확인한다.

응답 예시:

```json
{
  "success": true,
  "message": "서버가 정상적으로 동작 중입니다.",
  "data": {
    "status": "healthy"
  }
}
```

## Status

### GET /status

현재 욕실 상태와 활성 세션 정보를 조회한다.

응답 예시:

```json
{
  "success": true,
  "message": "Current status retrieved successfully.",
  "data": {
    "current_state": "ACTIVE",
    "last_door_state": "closed",
    "last_mmwave_detected": true,
    "last_zone": "toilet",
    "last_motion_level": 0.4,
    "last_still_time": 3,
    "last_reason": "Occupant movement was detected",
    "last_updated": "2026-05-26T12:00:00.000000",
    "waiting_for_response": false,
    "pending_response_type": null,
    "abnormal_start_time": null,
    "last_fall_detected": false,
    "last_fall_score": 0.0,
    "last_fall_at": null,
    "active_session": null
  }
}
```

## Sensor

### POST /sensor/mmwave

mmWave 센서의 감지 여부, 좌표, 움직임 정보를 수신한다. 수신된 데이터는 상태 판단,
세션 기록, feature 생성, 낙상 규칙 탐지, 이상탐지 모델 입력으로 사용된다.

요청 예시:

```json
{
  "detected": true,
  "x": 1.25,
  "y": 0.78,
  "z": 1.0,
  "motion_level": 0.42,
  "velocity": 0.12,
  "zone": "toilet",
  "still_time": 3
}
```

응답 data 주요 필드:

- `payload`: 정규화된 센서 입력
- `feature_vector`: ML 입력 feature
- `fall_detection`: 규칙 기반 낙상 판단 결과
- `anomaly`: 이상탐지 판단 결과
- `fusion_detection`: 낙상/이상탐지/상태 정보를 결합한 판단
- `status`: 처리 후 상태 스냅샷
- `session`: 연결된 활성 세션

### POST /sensor/door

도어 센서 상태를 수신한다.

요청 예시:

```json
{
  "door_state": "open"
}
```

`door_state` 값:

- `open`
- `closed`

## Device

### POST /device/button

사용자 버튼 입력을 처리한다.

요청 예시:

```json
{
  "button_type": "confirm_safe"
}
```

`button_type` 값:

- `confirm_safe`: 사용자가 안전함을 확인
- `emergency_call`: 사용자가 직접 긴급 호출
- `reset`: 상태 초기화

### POST /device/speaker

스피커 알림 요청을 등록한다.

요청 예시:

```json
{
  "message": "안전 확인 버튼을 눌러주세요.",
  "alert_level": "warning",
  "repeat": 3
}
```

`alert_level` 값:

- `info`
- `warning`
- `danger`

### POST /device/heartbeat

IoT 장치의 연결 상태를 보고한다.

요청 예시:

```json
{
  "device_name": "mmwave",
  "status": "online"
}
```

`device_name` 값:

- `mmwave`
- `door_sensor`
- `button`
- `speaker`

`status` 값:

- `online`
- `offline`
- `degraded`

### GET /device/status

최근 heartbeat 기준 장치 상태 목록을 조회한다.

## Calibration

### POST /calibration/start

존 캘리브레이션 세션을 시작한다.

요청 예시:

```json
{
  "user_id": "mobile_user"
}
```

### GET /calibration/status

현재 캘리브레이션 진행 상태를 조회한다.

### POST /calibration/step

현재 캘리브레이션 단계를 변경한다.

요청 예시:

```json
{
  "zone_name": "toilet"
}
```

`zone_name` 값:

- `toilet`
- `sink`
- `bath`

### POST /calibration/complete

특정 존의 캘리브레이션을 완료한다. `center_x`, `center_y`, `radius`를 전달하면
수동 보정으로 저장한다. 일부 값이 없으면 최근 mmWave 좌표 샘플을 사용해 자동 계산한다.

요청 예시:

```json
{
  "zone_name": "toilet",
  "center_x": 1.25,
  "center_y": 0.78,
  "radius": 0.7,
  "sample_limit": 20,
  "min_samples": 5,
  "radius_padding": 0.05
}
```

### POST /calibration/reset

캘리브레이션 진행 상태와 저장된 존 정보를 초기화한다.

### GET /calibration/zones

저장된 존 정보를 조회한다.

## Sessions

### GET /sessions

전체 세션 목록을 조회한다.

### GET /sessions/active

현재 활성 세션을 조회한다.

### POST /sessions/start

세션을 수동으로 시작한다.

### POST /sessions/end

활성 세션을 수동으로 종료한다.

## Alerts

### GET /alerts

생성된 알림 목록을 조회한다.

### GET /alerts/latest

가장 최근 알림을 조회한다.

## Anomalies

### GET /anomalies

현재 이상상황 여부, 최신 이상탐지 결과, 최신 알림 정보를 조회한다.

응답 data 주요 필드:

- `detected`: 현재 이상상황 여부
- `current_state`: 현재 상태
- `fall_detected`: 최근 낙상 규칙 탐지 여부
- `latest_prediction`: 최신 ML/heuristic 이상탐지 결과
- `latest_alert`: 최신 알림
- `alert_count`: 누적 알림 수

## Logs

### GET /logs

메모리에 저장된 시스템 로그 목록을 조회한다.

## Admin

### GET /admin/snapshot

운영/시연용 요약 스냅샷을 조회한다.

포함 정보:

- 현재 상태
- 활성 세션
- 장치 상태
- 알림 수
- 로그 수

### GET /admin/tuning

최근 mmWave 기록을 튜닝용 JSON 데이터로 조회한다.

쿼리 파라미터:

- `limit`: 조회 개수, 기본값 100, 최대 1000

### GET /admin/tuning.csv

최근 mmWave 기록을 CSV 파일로 내려받는다. 모델 튜닝, 센서 ROI 조정,
발표용 로그 분석에 사용한다.
