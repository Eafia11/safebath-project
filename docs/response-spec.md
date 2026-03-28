## 공통 응답 형식 (Common Response Format)

모든 API 응답은 아래와 같은 공통 구조를 사용한다.

### 성공 응답

success: true  
message: 요청이 정상적으로 처리되었습니다.  
data: {}  

---

### 실패 응답

success: false  
message: 잘못된 요청입니다.  
data: null  

---

### 필드 설명

- success: 요청 성공 여부를 나타냄 (true / false)  
- message: 요청 결과에 대한 설명 메시지  
- data: 실제 응답 데이터 (데이터가 없을 경우 빈 객체 {}, 실패 시 null 반환)  

---

### 규칙

- 모든 API는 success, message, data 필드를 반드시 포함해야 한다.  
- 요청이 성공한 경우 success는 true여야 한다.  
- 요청이 실패한 경우 success는 false여야 한다.  
- 반환할 데이터가 없는 경우 data는 {}로 설정한다.  
- 요청 실패 시 data는 null로 설정한다.  

---

### 응답 예시

#### 서버 상태 확인 (GET /health)

success: true  
message: 서버가 정상적으로 동작 중입니다.  
data:  
  status: healthy  

---

#### 현재 상태 조회 (GET /status)

success: true  
message: 현재 시스템 상태를 조회했습니다.  
data:  
  current_state: EMPTY  

---

#### 센서 데이터 수신 (POST /sensor/mmwave)

success: true  
message: mmWave 데이터 수신 완료  
data:  
  received: true  

---

#### 오류 발생 예시

success: false  
message: 필수 값이 누락되었습니다. (timestamp)  
data: null  