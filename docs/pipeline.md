# 전체 파이프라인 (End-to-End Pipeline)

이 문서는 SafeBath가 센서 입력을 받아 모바일 화면과 보호자 알림까지 연결하는 전체 흐름을
정리한다.

## 1. 정상 감지 파이프라인

```text
1. LD2450 센서가 사람의 위치/속도 데이터를 생성한다.
2. Raspberry Pi의 iot/ld2450_sender.py가 UART 프레임을 읽는다.
3. sender가 target을 필터링하고 대표 target을 선택한다.
4. sender가 /sensor/mmwave로 JSON 데이터를 전송한다.
5. FastAPI sensor router가 요청을 받는다.
6. sensor_service가 좌표 검증과 zone 판별을 수행한다.
7. feature_service가 ML feature vector를 만든다.
8. state_service가 현재 욕실 상태를 갱신한다.
9. session_service가 활성 세션을 생성하거나 갱신한다.
10. fall_detector가 낙상 규칙을 평가한다.
11. anomaly_service가 이상탐지를 수행한다.
12. fusion_detector가 판단 결과를 결합한다.
13. repository가 센서 기록, feature, 상태 snapshot을 저장한다.
14. 모바일 앱이 /status를 polling하여 최신 상태를 표시한다.
```

## 2. mmWave 입력 예시

IoT 장치가 백엔드로 보내는 payload:

```json
{
  "detected": true,
  "x": 1.25,
  "y": 0.78,
  "z": null,
  "motion_level": 0.12,
  "velocity": 0.12,
  "still_time": 3,
  "zone": null
}
```

백엔드는 `x`, `y` 좌표와 캘리브레이션된 존 정보를 이용해 `zone`을 보정한다.

## 3. 상태 판단 파이프라인

```text
door open
  -> ENTERING

mmWave detected=true
  -> ACTIVE 또는 TOILET_USE

zone=toilet
  -> TOILET_USE

detected=true + still_time 증가
  -> ABNORMAL

ABNORMAL + 사용자 응답 없음
  -> EMERGENCY + alert 생성

button_type=confirm_safe
  -> ACTIVE

button_type=reset
  -> EMPTY
```

## 4. 낙상 의심 파이프라인

```text
1. mmWave 샘플이 들어온다.
2. fall_detector가 이전 샘플과 현재 샘플을 비교한다.
3. height_drop, speed_change, still_time을 계산한다.
4. 세 조건이 기준값을 넘으면 낙상 의심으로 판단한다.
5. state_service가 상태를 ABNORMAL로 바꾼다.
6. speaker 요청을 생성한다.
7. 사용자가 confirm_safe를 누르면 ACTIVE로 복귀한다.
8. 응답이 없으면 EMERGENCY로 전환하고 보호자 알림을 만든다.
```

현재 기준값:

| 조건 | 기준 |
| --- | --- |
| 높이 변화 | `height_drop >= 0.35` |
| 속도 변화 | `speed_change >= 0.8` |
| 정지 시간 | `still_time >= 10` |
| 응답 대기 | 10초 |

## 5. 이상탐지 파이프라인

```text
mmWave request
  -> FeatureVector
  -> IsolationForest model
  -> AnomalyPrediction
  -> fusion_detector
  -> status / alert 판단에 참고
```

FeatureVector 주요 필드:

- `detected`
- `x`, `y`, `z`
- `motion_level`
- `velocity`
- `still_time`
- `distance_from_origin`
- `zone_score`
- `is_door_zone`
- `is_sink_zone`
- `is_toilet_zone`

모델이 학습되어 있지 않으면 `model_service`는 heuristic score를 사용한다.

## 6. 캘리브레이션 파이프라인

```text
1. 모바일 앱에서 보정 화면 진입
2. POST /calibration/start
3. toilet / sink / bath 중 현재 보정할 zone 선택
4. POST /calibration/step
5. 좌표와 반경을 수동 입력하거나 최근 mmWave 샘플로 자동 계산
6. POST /calibration/complete
7. 세 zone이 모두 완료되면 보정 세션 종료
8. 이후 mmWave 좌표는 zone_service에서 존 판별에 사용
```

수동 보정 예시:

```json
{
  "zone_name": "toilet",
  "center_x": 1.25,
  "center_y": 0.78,
  "radius": 0.7
}
```

자동 보정 예시:

```json
{
  "zone_name": "toilet",
  "sample_limit": 20,
  "min_samples": 5,
  "radius_padding": 0.05
}
```

## 7. 모바일 표시 파이프라인

```text
1. 앱 실행
2. GET /health로 서버 연결 확인
3. GET /status로 현재 상태 조회
4. 홈 화면에서 5초마다 /status polling
5. current_state를 BathState enum으로 매핑
6. 상태별 색상, 문구, 아이콘 표시
```

상태 매핑:

| Backend | Mobile |
| --- | --- |
| `EMPTY` | 사용 안 함 |
| `ENTERING` | 진입 중 |
| `ACTIVE` | 활동 중 |
| `TOILET_USE` | 변기 이용 중 |
| `ABNORMAL` | 이상 상태 감지 |
| `EMERGENCY` | 긴급 상황 |

## 8. 데이터 저장 파이프라인

```text
sensor_repository
  -> 원본 센서 payload, 상태, 낙상/이상탐지 결과 저장

feature_repository
  -> ML feature vector 저장

status_repository
  -> 상태 snapshot 저장

session_repository
  -> 욕실 사용 세션 저장

alert_repository
  -> 보호자 알림 저장

log_service
  -> 상태/센서/장치 이벤트 로그 저장
```

## 9. 발표용 핵심 흐름

정상 사용:

```text
센서 감지 -> ACTIVE -> TOILET_USE -> ACTIVE -> EMPTY
```

이상상황:

```text
센서 감지 -> ACTIVE -> still_time 증가 -> ABNORMAL -> EMERGENCY
```

보정:

```text
모바일 보정 시작 -> toilet/sink/bath 저장 -> /calibration/zones 확인
```

관리자 튜닝:

```text
센서 입력 누적 -> /admin/tuning.csv 다운로드 -> ROI/모델 튜닝
```
