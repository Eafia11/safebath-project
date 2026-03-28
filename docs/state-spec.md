## 상태 정의 (System State Definition)

시스템은 사용자의 화장실 이용 상태를 다음과 같은 상태로 구분한다.

---

### 상태 목록

- EMPTY  
  내부에 사용자가 존재하지 않는 상태  

- ENTERING  
  사용자가 화장실에 진입하는 것으로 추정되는 상태 (도어 열림 이후 mmWave 감지 시작)  

- ACTIVE  
  내부에서 움직임이 감지되는 일반 활동 상태  

- TOILET_USE  
  변기 존에서 일정 시간 이상 체류하는 상태  

- ABNORMAL  
  장시간 무반응 또는 비정상적인 체류 상태  

- EMERGENCY  
  위험 상황으로 판단되는 상태 (버튼 미응답, 장시간 정지 등)  

---

### 상태 설명

EMPTY 상태는 mmWave 센서에서 사용자가 감지되지 않을 때 유지된다.  

ENTERING 상태는 도어 센서가 열리고 이후 mmWave에서 사용자 감지가 시작될 때 전이된다.  

ACTIVE 상태는 내부에서 움직임이 지속적으로 감지되는 일반적인 사용 상태이다.  

TOILET_USE 상태는 특정 존(변기 위치)에서 일정 시간 이상 체류할 경우 전이된다.  

ABNORMAL 상태는 장시간 움직임이 없거나 일반적인 사용 패턴과 다른 경우 전이된다.  

EMERGENCY 상태는 ABNORMAL 상태 이후에도 사용자 반응이 없거나 위험 조건이 충족될 경우 전이된다.  

---

### 상태 전이 예시

EMPTY → ENTERING → ACTIVE → TOILET_USE → ACTIVE → EMPTY  

EMPTY → ENTERING → ACTIVE → ABNORMAL → EMERGENCY  

---

### 상태 판단 기준 (초기 규칙 기반)

- 도어 열림 이후 mmWave 감지 발생 → ENTERING  
- 지속적인 움직임 감지 → ACTIVE  
- 특정 존에서 일정 시간 이상 체류 → TOILET_USE  
- 일정 시간 이상 움직임 없음 → ABNORMAL  
- 경고 후 버튼 입력 없음 → EMERGENCY  

---

### 상태 정의 목적

- 사용자 행동을 명확하게 구분하기 위함  
- 이상행동 판단 기준을 단순화하기 위함  
- 향후 AI 기반 판단 로직 확장을 위한 기반 구조 제공  