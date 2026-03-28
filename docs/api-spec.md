## API 명세 (API Specification)

시스템은 다음과 같은 API 엔드포인트를 제공한다.

---

### 1. 서버 상태 확인

GET /health  

설명: 서버의 정상 동작 여부를 확인한다.  

응답 예시  

success: true  
message: 서버가 정상적으로 동작 중입니다.  
data:  
  status: healthy  

---

### 2. 현재 상태 조회

GET /status  

설명: 현재 시스템 상태를 반환한다.  

응답 예시  

success: true  
message: 현재 시스템 상태를 조회했습니다.  
data:  
  current_state: EMPTY  

---

### 3. mmWave 센서 데이터 수신

POST /sensor/mmwave  

설명: mmWave 센서로부터 사용자 위치 및 움직임 데이터를 수신한다.  

요청 예시  

timestamp: 2026-03-28T15:00:00  
detected: true  
x: 1.2  
y: 2.4  
motion_level: 0.7  
zone: toilet  
still_time: 10  

응답 예시  

success: true  
message: mmWave 데이터 수신 완료  
data:  
  received: true  

---

### 4. 도어 센서 데이터 수신

POST /sensor/door  

설명: 도어 센서로부터 출입 상태를 수신한다.  

요청 예시  

timestamp: 2026-03-28T15:00:03  
door_state: open  

응답 예시  

success: true  
message: 도어 센서 데이터 수신 완료  
data:  
  received: true  

---

### 5. 버튼 입력 처리

POST /device/button  

설명: 사용자 버튼 입력을 처리한다.  

요청 예시  

timestamp: 2026-03-28T15:02:00  
button_type: confirm_safe  

응답 예시  

success: true  
message: 버튼 입력 처리 완료  
data:  
  received: true  

---

### 6. 알림 생성

POST /alerts  

설명: 이상행동 또는 위험 상황 발생 시 알림을 생성한다.  

요청 예시  

timestamp: 2026-03-28T15:03:00  
level: warning  
message: 사용자 응답 없음  

응답 예시  

success: true  
message: 알림 생성 완료  
data:  
  created: true  


## 존 캘리브레이션 API (Calibration API)

존 캘리브레이션 API는 사용자의 실제 위치 정보를 기반으로 door, toilet, sink 존을 설정하기 위한 절차를 관리한다.  
현재 단계에서는 캘리브레이션 세션 관리 및 존 완료 상태를 처리하며, 추후 실제 mmWave 좌표 데이터와 연결하여 존 중심 좌표 및 범위를 계산하도록 확장한다.

---

### 1. 캘리브레이션 시작

POST /calibration/start

설명: 새로운 존 캘리브레이션 세션을 시작한다.  
초기 단계는 door 존부터 시작한다.

요청 예시

user_id: user_001

응답 예시

success: true  
message: 존 캘리브레이션을 시작했습니다.  
data:  
  is_active: true  
  user_id: user_001  
  current_step: door  
  started_at: 2026-03-28T16:00:00  
  completed_zones: []  
  progress: 0/3  

---

### 2. 캘리브레이션 상태 조회

GET /calibration/status

설명: 현재 캘리브레이션 진행 상태를 조회한다.

응답 예시

success: true  
message: 캘리브레이션 상태를 조회했습니다.  
data:  
  is_active: true  
  user_id: user_001  
  current_step: toilet  
  started_at: 2026-03-28T16:00:00  
  completed_zones:  
    - door  
  progress: 1/3  

---

### 3. 캘리브레이션 단계 변경

POST /calibration/step

설명: 현재 진행 중인 캘리브레이션 단계를 수동으로 변경한다.

요청 예시

zone_name: toilet

응답 예시

success: true  
message: 캘리브레이션 단계를 변경했습니다.  
data:  
  is_active: true  
  user_id: user_001  
  current_step: toilet  
  started_at: 2026-03-28T16:00:00  
  completed_zones:  
    - door  
  progress: 1/3  

---

### 4. 특정 존 캘리브레이션 완료

POST /calibration/complete

설명: 특정 존의 캘리브레이션을 완료 처리한다.  
현재 단계에서는 더미 저장 구조를 사용하며, 추후 실제 좌표 기반 중심점 및 반경 계산 결과를 저장하도록 확장한다.

요청 예시

zone_name: sink

응답 예시

success: true  
message: sink 존 캘리브레이션을 완료했습니다.  
data:  
  is_active: true  
  user_id: user_001  
  current_step: null  
  started_at: 2026-03-28T16:00:00  
  completed_zones:  
    - door  
    - toilet  
    - sink  
  progress: 3/3  

---

### 5. 캘리브레이션 초기화

POST /calibration/reset

설명: 현재 진행 중인 캘리브레이션 세션과 저장된 진행 상태를 초기화한다.

응답 예시

success: true  
message: 캘리브레이션을 초기화했습니다.  
data:  
  is_active: false  
  user_id: null  
  current_step: null  
  started_at: null  
  completed_zones: []  
  progress: 0/3  

---

### 6. 저장된 존 정보 조회

GET /calibration/zones

설명: 현재 저장된 존 정보를 조회한다.  
현재 단계에서는 center_x, center_y, radius를 더미 구조로 유지하며, 센서 연동 후 실제 계산값이 저장된다.

응답 예시

success: true  
message: 저장된 존 정보를 조회했습니다.  
data:  
  door:  
    center_x: null  
    center_y: null  
    radius: null  
    calibrated: true  
  toilet:  
    center_x: null  
    center_y: null  
    radius: null  
    calibrated: true  
  sink:  
    center_x: null  
    center_y: null  
    radius: null  
    calibrated: false  

---

### 캘리브레이션 대상 존

- door  
- toilet  
- sink  

---

### 캘리브레이션 활용 목적

- 사용자 위치별 존 정보를 사전에 정의하기 위함  
- mmWave 센서 좌표를 기반으로 자동 zone 판별을 수행하기 위함  
- 화장실 이용 상태 및 이상행동 판단의 정확도를 높이기 위함  
- 향후 비지도 학습 기반 이상행동 분석에 사용할 위치 feature를 안정적으로 확보하기 위함  