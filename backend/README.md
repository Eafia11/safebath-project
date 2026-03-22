# Backend - SafeBath Project

화장실 이용 패턴 기반 이상행동 및 위험 상황 감지 시스템의 백엔드 서버입니다.

---

## 역할
- IoT 장치로부터 센서 데이터 수신
- 수집 데이터 저장 및 관리
- 이상행동 및 위험 상황 분석
- 모바일 앱에 상태 및 결과 제공

---

## 기술 스택
- Python
- FastAPI
- Uvicorn
- Pydantic

---

## 폴더 구조

backend/
├─ app/
│  └─ main.py
├─ requirements.txt
├─ README.md
└─ .env.example

---

## 실행 방법

### 1. 가상환경 생성

python -m venv venv

### 2. 가상환경 활성화

venv\Scripts\activate

### 3. 라이브러리 설치

pip install -r requirements.txt

### 4. 서버 실행

uvicorn app.main:app --reload

---

## 현재 구현 상태
- FastAPI 기본 서버 실행 확인 완료
- 개발용 가상환경 및 requirements.txt 구성 완료

---

## 향후 개발 예정
- 센서 데이터 수신 API 설계
- 데이터 저장 구조 설계
- 이상행동 분석 로직 구현
- 모바일 앱 연동 API 구현

---

## 담당
- Backend: 홍성우