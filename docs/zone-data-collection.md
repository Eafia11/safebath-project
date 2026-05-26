# 60cm 모델 존 데이터 수집 절차

이 문서는 60 x 60 x 60cm 축소 욕실 모델에서 LD2450 센서 데이터를 수집하고
`empty`, `toilet`, `sink`, `bath` 라벨이 붙은 CSV를 만드는 절차를 정리한다.

## 목표

```text
라즈베리파이 LD2450 sender 실행
-> 백엔드 /sensor/mmwave 수신
-> /admin/tuning 기록 누적
-> 구간별 label 부여
-> data/raw/zone_collection_*.csv 생성
```

## 1. 좌표계 고정

먼저 모델에서 좌표 기준을 정한다.

권장 기준:

- 센서 위치를 원점 또는 기준점으로 둔다.
- `x`: 좌우 방향
- `y`: 센서에서 멀어지는 방향
- `z`: 높이 방향
- 단위는 백엔드 기준에 맞춰 meter를 사용한다.

60cm 모델 기준:

```text
0cm ~ 60cm = 0.00m ~ 0.60m
```

수집 전에 아래 값을 메모한다.

| 항목 | 값 |
| --- | --- |
| 센서 위치 |  |
| 센서 높이 |  |
| 모델 크기 | 60 x 60 x 60cm |
| toilet 중심 좌표 |  |
| sink 중심 좌표 |  |
| bath 중심 좌표 |  |
| 사용 포트 |  |
| 백엔드 주소 |  |

## 2. 백엔드 실행

PC 또는 AWS/서버에서 백엔드를 실행한다.

로컬 PC에서 라즈베리파이 접속을 받을 때:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --reload
```

확인:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/status
```

## 3. 라즈베리파이 sender 실행

라즈베리파이에서 백엔드 주소와 API key를 설정한다.

```bash
export SAFEBATH_BACKEND_URL=http://43.201.28.192:8000
export SAFEBATH_API_KEY=YOUR_API_KEY
```

LD2450 sender를 실행한다.

```bash
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

센서 포트가 다르면 다음으로 확인한다.

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

sender 터미널에서 `sent detected=... state=...` 로그가 계속 출력되면 준비 완료다.

## 4. 라벨 수집 스크립트 실행

PC에서 다른 터미널을 열고 다음을 실행한다.

```bash
python scripts/collect_zone_data.py --backend-url http://43.201.28.192:8000 --duration 30
```

API key가 있으면:

```bash
python scripts/collect_zone_data.py --backend-url http://43.201.28.192:8000 --api-key YOUR_API_KEY --duration 30
```

기본 수집 라벨:

```text
empty
toilet
sink
bath
toilet_to_sink
toilet_to_bath
abnormal
```

라벨을 직접 지정할 수도 있다.

```bash
python scripts/collect_zone_data.py --labels empty toilet sink bath --duration 45
```

## 5. 실제 수집 순서

스크립트가 각 라벨마다 Enter를 기다린다.

추천 순서:

1. `empty`: 모델 안에 target을 두지 않는다.
2. `toilet`: toilet 위치에 target을 둔다.
3. `sink`: sink 위치에 target을 둔다.
4. `bath`: bath 위치에 target을 둔다.
5. `toilet_to_sink`: toilet에서 sink 방향으로 천천히 이동한다.
6. `toilet_to_bath`: toilet에서 bath 방향으로 천천히 이동한다.
7. `abnormal`: toilet 또는 bath 근처에 target을 두고 움직이지 않는다.

각 단계마다 target을 배치한 뒤 Enter를 누른다.

## 6. 결과 파일

수집이 끝나면 다음 형태의 파일이 생성된다.

```text
data/raw/zone_collection_YYYYMMDD_HHMMSS.csv
```

주요 컬럼:

- `label`
- `timestamp`
- `detected`
- `x`, `y`, `z`
- `zone`
- `motion_level`
- `velocity`
- `still_time`
- `current_state`
- `fall_detected`
- `anomaly_detected`
- `anomaly_score`

## 7. 성공 기준

최소 성공 기준:

- 각 라벨별 데이터가 20개 이상 저장됨
- `toilet`, `sink`, `bath`의 좌표 분포가 서로 어느 정도 분리됨
- 백엔드 `/status`가 `ACTIVE` 또는 `TOILET_USE` 등으로 반영됨
- AWS 또는 로컬 로그에서 `/sensor/mmwave` 수신 기록 확인 가능

권장 성공 기준:

- 각 라벨별 데이터 50개 이상
- `empty`에서는 `detected=false` 비율이 높음
- 정지 시나리오에서 `still_time` 증가 확인
- `/admin/tuning.csv`로도 같은 기록 확인 가능

## 8. 수집 후 해야 할 일

1. CSV를 열어 label별 record 수를 확인한다.
2. `x`, `y` 좌표 분포를 확인한다.
3. toilet/sink/bath 중심 좌표와 반경을 정한다.
4. `/calibration/complete`로 존 정보를 저장한다.
5. 다시 sender를 실행해 zone 판별이 맞는지 확인한다.

수동 캘리브레이션 예시:

```bash
curl -X POST http://localhost:8000/calibration/start \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"zone_collection\"}"

curl -X POST http://localhost:8000/calibration/complete \
  -H "Content-Type: application/json" \
  -d "{\"zone_name\":\"toilet\",\"center_x\":0.30,\"center_y\":0.35,\"radius\":0.10}"
```

## 9. 문제 해결

데이터가 거의 저장되지 않을 때:

- sender가 실행 중인지 확인한다.
- `/admin/tuning?limit=10` 응답을 확인한다.
- API key가 맞는지 확인한다.

좌표가 계속 튈 때:

- `--debug-targets` 출력에서 T1/T2/T3를 확인한다.
- `--roi-y-min`, `--roi-y-max`, `--roi-x-limit`를 조정한다.
- 센서 각도와 target 반사 상태를 확인한다.

존이 구분되지 않을 때:

- 모델 내 각 zone 간 거리를 더 벌린다.
- target을 각 zone 중심에 더 오래 고정한다.
- radius를 너무 크게 잡지 않는다.
