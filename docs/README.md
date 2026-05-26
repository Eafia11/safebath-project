# SafeBath 문서 인덱스

SafeBath 프로젝트의 설계, API, 상태 전이, 로그, 시연 절차를 정리한 문서 모음이다.

## 추천 읽는 순서

1. [architecture.md](architecture.md): 시스템 구성과 각 모듈 역할
2. [pipeline.md](pipeline.md): 센서 입력부터 모바일 표시까지 전체 파이프라인
3. [demo-scenarios.md](demo-scenarios.md): 발표/시연용 절차
4. [setup-checklist.md](setup-checklist.md): 실행 및 발표 전 점검 목록
5. [zone-data-collection.md](zone-data-collection.md): 60cm 모델 존 데이터 수집 절차
6. [api-spec.md](api-spec.md): 백엔드 API 명세
7. [state-spec.md](state-spec.md): 상태 정의와 전이 규칙
8. [logging-spec.md](logging-spec.md): 로그 구조와 튜닝 데이터
9. [response-spec.md](response-spec.md): 공통 응답 형식

## 문서별 목적

| 문서 | 목적 |
| --- | --- |
| `architecture.md` | 전체 시스템 구조와 백엔드 내부 계층 설명 |
| `pipeline.md` | IoT, 백엔드, ML, 모바일이 연결되는 처리 흐름 설명 |
| `demo-scenarios.md` | 발표에서 그대로 따라 할 수 있는 시나리오 제공 |
| `setup-checklist.md` | 실행 환경, 테스트, 모바일, IoT, Docker 점검 |
| `zone-data-collection.md` | 60cm 모델에서 존 라벨 데이터를 수집하는 절차 |
| `api-spec.md` | 실제 FastAPI 라우터 기준 엔드포인트 정리 |
| `state-spec.md` | `EMPTY`부터 `EMERGENCY`까지 상태 정의 |
| `logging-spec.md` | 로그 종류, 저장 위치, 튜닝 데이터 확인 방법 |
| `response-spec.md` | API 응답 구조와 클라이언트 처리 기준 |

## 발표에서 강조할 핵심 문장

SafeBath는 LD2450 mmWave 센서 데이터를 백엔드로 전송하고, 상태 머신과 이상탐지 로직을
통해 욕실 사용자의 현재 상태를 판단한 뒤 모바일 앱에서 실시간으로 확인할 수 있게 하는
IoT 기반 욕실 안전 모니터링 시스템이다.
