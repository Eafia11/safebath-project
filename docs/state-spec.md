# 상태 정의 및 전이 규칙 (State Specification)

SafeBath는 욕실 사용 상황을 상태 머신으로 관리한다. 상태는 모바일 대시보드 표시,
이상상황 판단, 보호자 알림, 세션 기록의 기준이 된다.

## 상태 목록

| 상태 | 의미 |
| --- | --- |
| `EMPTY` | 욕실 내부에 사용자가 없다고 판단되는 상태 |
| `ENTERING` | 도어 열림 등으로 사용자가 진입 중이라고 판단되는 상태 |
| `ACTIVE` | 사용자가 욕실 안에서 정상적으로 활동 중인 상태 |
| `TOILET_USE` | 사용자가 변기 존에 머무르는 상태 |
| `ABNORMAL` | 장시간 정지, 낙상 의심 등 확인이 필요한 상태 |
| `EMERGENCY` | 사용자 응답 없음 또는 긴급 호출로 보호자 대응이 필요한 상태 |

## 핵심 입력

| 입력 | 출처 | 주요 필드 |
| --- | --- | --- |
| 도어 이벤트 | `/sensor/door` | `door_state` |
| mmWave 이벤트 | `/sensor/mmwave` | `detected`, `x`, `y`, `z`, `motion_level`, `velocity`, `zone`, `still_time` |
| 버튼 이벤트 | `/device/button` | `button_type` |
| 낙상 규칙 결과 | `fall_detector` | `detected`, `score`, `height_drop`, `speed_change` |
| 이상탐지 결과 | `anomaly_service` | `detected`, `score`, `reason` |

## 기본 전이

```text
EMPTY -> ENTERING -> ACTIVE -> TOILET_USE -> ACTIVE -> EMPTY
EMPTY -> ENTERING -> ACTIVE -> ABNORMAL -> EMERGENCY
ACTIVE -> EMERGENCY
ABNORMAL -> ACTIVE
```

## 전이 규칙

| 조건 | 다음 상태 | 설명 |
| --- | --- | --- |
| 도어가 열림 | `ENTERING` | 사용자가 욕실에 진입할 가능성이 있다고 판단 |
| 도어가 닫혔고 mmWave 미감지 | `EMPTY` | 사용자가 욕실 밖으로 나간 것으로 판단 |
| mmWave가 사용자를 감지하고 움직임이 있음 | `ACTIVE` | 정상 활동 상태 |
| mmWave가 `toilet` 존을 감지 | `TOILET_USE` | 변기 사용 상태 |
| 사용자가 감지되지만 일정 시간 움직임 없음 | `ABNORMAL` | 스피커 안내와 사용자 응답 대기 시작 |
| 낙상 규칙 조건 충족 | `ABNORMAL` | 낙상 의심 상태로 사용자 응답 대기 시작 |
| `ABNORMAL` 이후 응답 대기 시간 초과 | `EMERGENCY` | 보호자 대상 danger 알림 생성 |
| 사용자가 `confirm_safe` 버튼 입력 | `ACTIVE` | 안전 확인 후 정상 상태 복귀 |
| 사용자가 `emergency_call` 버튼 입력 | `EMERGENCY` | 사용자가 직접 긴급 호출 |
| 사용자가 `reset` 버튼 입력 | `EMPTY` | 상태 초기화 |

## 응답 대기 규칙

`ABNORMAL` 상태가 되면 시스템은 `waiting_for_response=true`로 전환한다.

응답 대기 유형:

- `inactivity`: 장시간 무동작
- `fall`: 낙상 의심

현재 구현 기준 응답 대기 제한 시간은 10초이다. 제한 시간 안에 사용자가
`confirm_safe` 버튼을 누르지 않으면 `EMERGENCY`로 전이하고 알림을 생성한다.

## 낙상 의심 규칙

낙상 규칙은 다음 조건을 함께 본다.

- 높이 변화량 `height_drop >= 0.35`
- 속도 변화량 `speed_change >= 0.8`
- 정지 시간 `still_time >= 10`
- mmWave가 사용자를 감지 중

모든 조건이 충족되면 `fall_detector`는 낙상 의심으로 판단하고, 상태는
`ABNORMAL`로 바뀐다.

## 상태 스냅샷 필드

`GET /status`는 다음 정보를 반환한다.

| 필드 | 설명 |
| --- | --- |
| `current_state` | 현재 상태 |
| `last_door_state` | 최근 도어 상태 |
| `last_mmwave_detected` | 최근 mmWave 감지 여부 |
| `last_zone` | 최근 감지 존 |
| `last_motion_level` | 최근 움직임 강도 |
| `last_still_time` | 최근 정지 시간 |
| `last_reason` | 현재 상태가 된 이유 |
| `last_updated` | 최근 상태 갱신 시각 |
| `waiting_for_response` | 사용자 응답 대기 여부 |
| `pending_response_type` | 응답 대기 유형 |
| `abnormal_start_time` | 이상상황 시작 시각 |
| `last_fall_detected` | 최근 낙상 규칙 탐지 여부 |
| `last_fall_score` | 최근 낙상 점수 |
| `last_fall_at` | 최근 낙상 의심 시각 |

## 발표용 대표 시나리오

정상 사용:

```text
door open -> ENTERING
mmWave detected -> ACTIVE
zone toilet -> TOILET_USE
movement resumes -> ACTIVE
door closed + no detection -> EMPTY
```

장시간 정지:

```text
ACTIVE
still_time 증가 -> ABNORMAL
사용자 응답 없음 -> EMERGENCY
```

낙상 의심:

```text
ACTIVE
height_drop + speed_change + still_time 조건 충족 -> ABNORMAL
사용자 응답 없음 -> EMERGENCY
```
