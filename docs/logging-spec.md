## 로그 구조 (Logging Structure)

시스템의 동작을 추적하고 디버깅 및 상태 분석을 위해 다음과 같은 로그 구조를 사용한다.

---

### 1. 시스템 로그 (System Log)

서버 실행, 종료, 에러 등의 시스템 이벤트를 기록한다.

timestamp: 2026-03-28T14:00:00  
type: system  
level: info  
message: server started  

---

### 2. 센서 로그 (Sensor Log)

mmWave, 도어 센서, 버튼 등 입력 데이터를 기록한다.

timestamp: 2026-03-28T14:01:00  
type: sensor  
sensor: mmwave  
payload:  
  detected: true  
  x: 1.3  
  y: 2.1  
  motion_level: 0.72  
  zone: toilet  

---

### 3. 상태 변화 로그 (State Log)

시스템 상태가 변경될 때 기록한다.

timestamp: 2026-03-28T14:01:05  
type: state  
previous_state: EMPTY  
current_state: ACTIVE  
reason: mmwave detected after door close  

---

### 4. 알림/경고 로그 (Alert Log)

이상행동 감지 및 경고 발생 이벤트를 기록한다.

timestamp: 2026-03-28T14:05:00  
type: alert  
level: warning  
message: 사용자 응답 없음  
action: speaker warning triggered  

---

### 로그 필드 설명

- timestamp: 로그 발생 시각 (ISO 8601 형식)  
- type: 로그 종류 (system, sensor, state, alert)  
- level: 로그 중요도 (info, warning, error)  
- sensor: 센서 종류 (mmwave, door, button 등)  
- payload: 센서 입력 데이터  
- previous_state: 이전 상태  
- current_state: 현재 상태  
- reason: 상태 변경 이유  
- message: 로그 메시지  
- action: 수행된 동작  

---

### 로그 유형 정리

- system: 서버 및 시스템 이벤트  
- sensor: 센서 입력 데이터  
- state: 상태 변화 기록  
- alert: 이상행동 및 경고 이벤트  