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