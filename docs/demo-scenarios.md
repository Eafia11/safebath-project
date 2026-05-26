# 시연 시나리오 (Demo Scenarios)

이 문서는 발표 또는 중간 점검에서 SafeBath를 안정적으로 보여주기 위한 시나리오를 정리한다.

## 사전 준비

백엔드 실행:

```bash
uvicorn backend.app.main:app --reload
```

상태 확인:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

API key를 사용하는 경우:

```bash
curl -H "x-api-key: YOUR_API_KEY" http://localhost:8000/admin/snapshot
```

## 시나리오 1. 서버 정상 동작 확인

목표:

- 백엔드가 정상 실행 중임을 보여준다.
- Swagger 문서가 열리는 것을 보여준다.

절차:

```text
1. 백엔드 실행
2. /health 호출
3. /docs 접속
4. /status 호출
```

성공 기준:

- `/health` 응답의 `data.status`가 `healthy`
- `/status`에서 현재 상태가 조회됨

## 시나리오 2. 정상 욕실 사용 흐름

목표:

- 도어 이벤트와 mmWave 이벤트로 상태가 정상 전이되는 것을 보여준다.

절차:

```bash
curl -X POST http://localhost:8000/sensor/door \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d "{\"door_state\":\"open\"}"

curl -X POST http://localhost:8000/sensor/mmwave \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d "{\"detected\":true,\"x\":1.25,\"y\":0.78,\"motion_level\":0.5,\"velocity\":0.2,\"zone\":\"toilet\",\"still_time\":1}"

curl http://localhost:8000/status
```

성공 기준:

- 도어 열림 후 `ENTERING`
- mmWave 감지 후 `ACTIVE` 또는 `TOILET_USE`
- 모바일 홈 화면에 현재 상태 반영

## 시나리오 3. 장시간 정지 이상상황

목표:

- 사용자가 움직이지 않는 상황에서 `ABNORMAL` 또는 `EMERGENCY` 흐름을 보여준다.

절차:

```bash
curl -X POST http://localhost:8000/sensor/mmwave \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d "{\"detected\":true,\"x\":1.25,\"y\":0.78,\"motion_level\":0.0,\"velocity\":0.0,\"zone\":\"toilet\",\"still_time\":30}"

curl http://localhost:8000/status
curl http://localhost:8000/anomalies
curl http://localhost:8000/alerts/latest
```

성공 기준:

- 상태가 `ABNORMAL` 또는 `EMERGENCY`로 전환됨
- `waiting_for_response`가 true가 되거나 알림이 생성됨

## 시나리오 4. 사용자 안전 확인

목표:

- 이상상황 후 사용자가 안전 확인 버튼을 누르면 정상 상태로 복귀하는 것을 보여준다.

절차:

```bash
curl -X POST http://localhost:8000/device/button \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d "{\"button_type\":\"confirm_safe\"}"

curl http://localhost:8000/status
```

성공 기준:

- `waiting_for_response=false`
- `current_state=ACTIVE`

## 시나리오 5. 긴급 호출

목표:

- 사용자가 직접 긴급 호출 버튼을 누르면 보호자 알림이 생성되는 것을 보여준다.

절차:

```bash
curl -X POST http://localhost:8000/device/button \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d "{\"button_type\":\"emergency_call\"}"

curl http://localhost:8000/status
curl http://localhost:8000/alerts/latest
```

성공 기준:

- `current_state=EMERGENCY`
- 최신 알림의 `level=danger`

## 시나리오 6. 존 캘리브레이션

목표:

- 모바일 또는 API로 toilet, sink, bath 존을 설정하는 흐름을 보여준다.

절차:

```bash
curl -X POST http://localhost:8000/calibration/start \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"mobile_user\"}"

curl -X POST http://localhost:8000/calibration/complete \
  -H "Content-Type: application/json" \
  -d "{\"zone_name\":\"toilet\",\"center_x\":1.25,\"center_y\":0.78,\"radius\":0.7}"

curl -X POST http://localhost:8000/calibration/complete \
  -H "Content-Type: application/json" \
  -d "{\"zone_name\":\"sink\",\"center_x\":2.1,\"center_y\":0.95,\"radius\":0.7}"

curl -X POST http://localhost:8000/calibration/complete \
  -H "Content-Type: application/json" \
  -d "{\"zone_name\":\"bath\",\"center_x\":1.7,\"center_y\":1.2,\"radius\":0.7}"

curl http://localhost:8000/calibration/zones
```

성공 기준:

- `progress=3/3`
- 각 존에 `calibrated=true`

## 시나리오 7. 실제 LD2450 센서 연동

목표:

- Raspberry Pi에서 센서 데이터를 읽어 백엔드와 모바일까지 연결되는 것을 보여준다.

절차:

```bash
export SAFEBATH_BACKEND_URL=http://YOUR_PC_IP:8000
export SAFEBATH_API_KEY=YOUR_API_KEY
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

성공 기준:

- 터미널에 target 좌표와 전송 결과 출력
- 백엔드 `/status`에 감지 상태 반영
- 모바일 앱 홈 화면 상태 변경

## 시나리오 8. 튜닝 데이터 확인

목표:

- 센서 입력이 분석 가능한 데이터로 쌓이는 것을 보여준다.

절차:

```bash
curl -H "x-api-key: YOUR_API_KEY" "http://localhost:8000/admin/tuning?limit=20"
curl -H "x-api-key: YOUR_API_KEY" -o safebath_tuning.csv "http://localhost:8000/admin/tuning.csv?limit=100"
```

성공 기준:

- 최근 mmWave 기록이 JSON/CSV로 조회됨
- 좌표, 상태, 낙상/이상탐지 결과가 함께 포함됨
