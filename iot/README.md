# SafeBath IoT

이 디렉터리는 Raspberry Pi에서 LD2450 mmWave 센서 데이터를 읽고 SafeBath 백엔드로
전송하기 위한 스크립트를 담고 있다.

## 구성 파일

- `ld2450_sender.py`: LD2450 UART 프레임을 읽어 `/sensor/mmwave`로 전송하는 메인 스크립트
- `requirements.txt`: Raspberry Pi에서 필요한 최소 Python 의존성
- `example.py`: IoT 예제 코드

## 동작 흐름

```text
LD2450 Sensor
  -> Raspberry Pi serial port
  -> iot/ld2450_sender.py
  -> POST /sensor/mmwave
  -> Backend state/anomaly pipeline
  -> Mobile dashboard / AWS logs
```

## Raspberry Pi 준비

Raspberry Pi에서 프로젝트 디렉터리로 이동한 뒤 IoT 전용 가상환경을 만든다.

```bash
cd ~/safebath-project
python3 -m venv iot-venv
source iot-venv/bin/activate
pip install -r iot/requirements.txt
```

## 백엔드 준비

PC에서 백엔드를 받을 경우 외부 접속 가능하게 실행한다.

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --reload
```

AWS 백엔드를 사용할 경우 실행 중인 백엔드 주소를 준비한다.

## 센서 포트 확인

LD2450이 어떤 serial 포트로 잡혔는지 확인한다.

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

자주 사용하는 포트:

- `/dev/ttyUSB0`
- `/dev/ttyACM0`

## LD2450 sender 실행

백엔드 주소를 환경 변수로 설정한다.

```bash
export SAFEBATH_BACKEND_URL=http://43.201.28.192:8000
```

백엔드에 `API_KEY`가 설정되어 있으면 API key도 함께 설정한다.

```bash
export SAFEBATH_API_KEY=YOUR_API_KEY
```

sender를 실행한다.

```bash
python3 iot/ld2450_sender.py --port /dev/ttyUSB0
```

기본 전송 주기는 약 0.3초다. 전송 주기를 바꾸려면 `--interval`을 사용한다.

```bash
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --interval 0.5
```

## 디버그 모드

존 보정이나 센서 위치 조정 중에는 `--debug-targets`를 사용한다.

```bash
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

출력 예시:

```text
2026-05-26T14:03:12 sent detected=True target=T1 x=0.31 y=0.42 velocity=0.08 state=ACTIVE
  T1(x=0.310, y=0.420, v=0.08, d=0.522, ok) | T2=none | T3=none
```

## 주요 옵션

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `--port` | LD2450 serial 포트 | `/dev/ttyUSB0` |
| `--baud` | serial baud rate | `256000` |
| `--interval` | 백엔드 전송 주기(초) | `0.3` |
| `--debug-targets` | 모든 target과 선택 결과 출력 | off |
| `--roi-y-min` | 유효 y 최소값(mm) | `0` |
| `--roi-y-max` | 유효 y 최대값(mm) | `600` |
| `--roi-x-limit` | 유효 x 절댓값 최대(mm) | `300` |
| `--space-x-min` | 60cm 모델 공간 x 최소값(mm) | `-300` |
| `--space-x-max` | 60cm 모델 공간 x 최대값(mm) | `300` |
| `--space-y-min` | 60cm 모델 공간 y 최소값(mm) | `0` |
| `--space-y-max` | 60cm 모델 공간 y 최대값(mm) | `600` |
| `--max-speed-cm-s` | 허용 속도 최대값(cm/s) | `150` |
| `--stale-seconds` | 같은 값이 반복되는 정지 target 제외 시간 | `3.0` |
| `--prefer-moving` | 움직이는 target을 우선 선택 | off |
| `--allow-out-of-space` | 공간 밖 target도 선택/전송 허용 | off |

환경 변수로도 설정할 수 있다.

```bash
export LD2450_PORT=/dev/ttyUSB0
export LD2450_BAUD=256000
export LD2450_SEND_INTERVAL=0.3
export LD2450_ROI_Y_MIN=0
export LD2450_ROI_Y_MAX=600
export LD2450_ROI_X_LIMIT=300
export LD2450_SPACE_X_MIN=-300
export LD2450_SPACE_X_MAX=300
export LD2450_SPACE_Y_MIN=0
export LD2450_SPACE_Y_MAX=600
export LD2450_MAX_SPEED_CM_S=150
export LD2450_STALE_SECONDS=3.0
```

`--debug-targets`를 켜면 T1~T3가 표 형태로 표시된다. `*T1`처럼 별표가 붙은 target이
백엔드로 전송되는 대표 target이다.

```text
  +--------+--------+--------+--------+----------+----------------+
  | target | x(m)   | y(m)   | v(m/s) | dist(m)  | status         |
  +--------+--------+--------+--------+----------+----------------+
  | *T1    |  0.120 |  0.350 |   0.04 |    0.370 | selected       |
  | T2     |  0.520 |  0.880 |   0.00 |    1.023 | out_space     |
  | T3     | none   | none   | none   | none     | none           |
  +--------+--------+--------+--------+----------+----------------+
```

`out_space`는 60cm 모델 공간 밖으로 판단되어 전송 대상에서 제외된 target이다.

## 60cm 모델 존 데이터 수집

60 x 60 x 60cm 축소 모델에서 `toilet`, `sink`, `bath` 데이터를 수집할 때는
sender를 먼저 실행한 뒤 PC에서 라벨 수집 스크립트를 실행한다.

Raspberry Pi:

```bash
export SAFEBATH_BACKEND_URL=http://43.201.28.192:8000
export SAFEBATH_API_KEY=YOUR_API_KEY
python3 iot/ld2450_sender.py --port /dev/ttyUSB0 --debug-targets
```

PC:

```bash
python scripts/collect_zone_data.py --backend-url http://43.201.28.192:8000 --api-key YOUR_API_KEY --duration 30
```

결과 파일:

```text
data/raw/zone_collection_YYYYMMDD_HHMMSS.csv
```

자세한 절차는 `docs/zone-data-collection.md`를 참고한다.

## 백엔드 수신 확인

상태 확인:

```bash
curl http://43.201.28.192:8000/status
```

최근 튜닝 데이터 확인:

```bash
curl -H "x-api-key: YOUR_API_KEY" "http://43.201.28.192:8000/admin/tuning?limit=10"
```

CSV 다운로드:

```bash
curl -H "x-api-key: YOUR_API_KEY" -o safebath_tuning.csv "http://43.201.28.192:8000/admin/tuning.csv?limit=100"
```

## 문제 해결

### serial 포트가 열리지 않을 때

- `/dev/ttyUSB0`, `/dev/ttyACM0` 중 실제 포트를 확인한다.
- 권한 문제가 있으면 `dialout` 그룹 권한을 확인한다.
- USB 케이블과 전원 공급을 확인한다.

### 서버 연결 실패가 날 때

- `SAFEBATH_BACKEND_URL`이 `localhost`가 아니라 PC 또는 AWS 주소인지 확인한다.
- PC 백엔드는 `--host 0.0.0.0`으로 실행했는지 확인한다.
- 같은 네트워크인지 확인한다.
- 방화벽에서 8000 포트를 허용했는지 확인한다.
- API key를 사용하는 경우 `SAFEBATH_API_KEY`가 맞는지 확인한다.

### target이 계속 none일 때

- `--debug-targets`로 T1/T2/T3 raw target을 확인한다.
- 센서 방향과 높이를 조정한다.
- target이 ROI 밖에 있으면 `--roi-y-min`, `--roi-y-max`, `--roi-x-limit`를 조정한다.

### 좌표가 너무 튈 때

- 센서를 고정한다.
- 반사체나 금속 물체를 치운다.
- `--prefer-moving` 옵션을 테스트한다.
- `--stale-seconds` 값을 조정한다.
