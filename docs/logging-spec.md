# 로그 구조 (Logging Specification)

SafeBath는 센서 입력, 상태 전이, 이상상황, 장치 이벤트를 로그로 남긴다. 로그는
디버깅, 발표 시연 검증, 센서/모델 튜닝에 사용된다.

## 로그 저장 위치

현재 구현에서 주요 런타임 로그는 `log_service`의 메모리 리스트에 저장되고
`GET /logs`로 조회한다. 센서 기록, feature, status snapshot, alert, session은 각
repository에 저장된다.

로컬 실행 시 영구 저장이 필요한 데이터는 `data/` 디렉터리를 사용한다.

Docker 실행 시 `safebath-data` 볼륨을 `/app/data`에 연결한다.

## 로그 기본 필드

| 필드 | 설명 |
| --- | --- |
| `timestamp` | 로그 발생 시각, ISO 8601 문자열 |
| `type` | 로그 종류 |
| `level` | 로그 중요도 |
| `message` | 로그 메시지 |
| `data` | 로그별 세부 payload |

## 로그 유형

| type | 발생 위치 | 설명 |
| --- | --- | --- |
| `sensor` | `state_service`, `sensor_service` | mmWave/door 입력 수신 |
| `state` | `state_service` | 상태 전이 |
| `alert` | `state_service`, `alert_service` | 이상상황, 긴급 알림, 스피커 안내 |
| `device` | `device_service`, `state_service` | 버튼, 스피커, heartbeat |
| `sensor_service` | `sensor_service` | 센서 처리 파이프라인 결과 요약 |

## 센서 로그

mmWave 또는 도어 이벤트가 들어오면 센서 로그가 기록된다.

예시:

```json
{
  "timestamp": "2026-05-26T12:00:00.000000",
  "type": "sensor",
  "level": "info",
  "message": "mmWave sensor event received",
  "data": {
    "detected": true,
    "zone": "toilet",
    "motion_level": 0.42,
    "still_time": 3
  }
}
```

## 상태 변화 로그

상태가 변경될 때 이전 상태, 새 상태, 변경 이유를 기록한다.

예시:

```json
{
  "timestamp": "2026-05-26T12:00:05.000000",
  "type": "state",
  "level": "info",
  "message": "State changed",
  "data": {
    "previous_state": "ACTIVE",
    "current_state": "ABNORMAL",
    "reason": "Possible fall detected; waiting for user response"
  }
}
```

## 알림 로그

장시간 무응답, 낙상 의심, 긴급 버튼 입력 등 보호자 대응이 필요한 경우 기록한다.

예시:

```json
{
  "timestamp": "2026-05-26T12:00:15.000000",
  "type": "alert",
  "level": "warning",
  "message": "Emergency alert created after no response",
  "data": {
    "alert": {
      "type": "emergency",
      "level": "danger",
      "target": "guardian",
      "message": "No user response after abnormal activity; emergency alert created."
    }
  }
}
```

## 장치 로그

버튼 입력, 스피커 요청, heartbeat가 들어오면 장치 이벤트로 기록한다.

예시:

```json
{
  "timestamp": "2026-05-26T12:00:20.000000",
  "type": "device",
  "level": "info",
  "message": "Button input received",
  "data": {
    "button_type": "confirm_safe"
  }
}
```

## 센서 처리 요약 로그

`sensor_service`는 mmWave 처리 후 다음 요약 정보를 남긴다.

```json
{
  "type": "sensor_service",
  "message": "mmWave event processed",
  "data": {
    "sensor": "mmwave",
    "resolved_zone": "toilet",
    "anomaly_detected": false,
    "fall_detected": false,
    "current_state": "TOILET_USE",
    "anomaly_reason": "score below threshold"
  }
}
```

## 튜닝 데이터

센서 튜닝과 모델 분석에는 `/admin/tuning` 또는 `/admin/tuning.csv`를 사용한다.

주요 컬럼:

- `timestamp`
- `session_id`
- `detected`
- `x`, `y`, `z`
- `zone`
- `motion_level`
- `velocity`
- `still_time`
- `current_state`
- `fall_detected`
- `fall_score`
- `anomaly_detected`
- `anomaly_score`
- `anomaly_reason`

## 확인 방법

로그 조회:

```bash
curl http://localhost:8000/logs
```

튜닝 데이터 조회:

```bash
curl -H "x-api-key: YOUR_API_KEY" "http://localhost:8000/admin/tuning?limit=50"
```

CSV 다운로드:

```bash
curl -H "x-api-key: YOUR_API_KEY" -o safebath_tuning.csv "http://localhost:8000/admin/tuning.csv?limit=200"
```
