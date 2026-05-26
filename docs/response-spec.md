# 공통 응답 형식 (Common Response Format)

SafeBath 백엔드는 일반 API 응답에 공통 구조를 사용한다. 모바일 앱과 IoT 장치는
이 구조를 기준으로 성공 여부와 실제 데이터를 해석한다.

## 성공 응답

```json
{
  "success": true,
  "message": "요청이 정상적으로 처리되었습니다.",
  "data": {}
}
```

## 실패 응답

애플리케이션 레벨에서 직접 생성하는 실패 응답은 다음 구조를 따른다.

```json
{
  "success": false,
  "message": "잘못된 요청입니다.",
  "data": null
}
```

FastAPI/Pydantic 검증 오류나 `HTTPException`은 FastAPI 기본 오류 형식으로 반환될 수 있다.
예를 들어 요청 body가 잘못되면 HTTP 422 응답이 발생한다.

## 필드 설명

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `success` | boolean | 요청 처리 성공 여부 |
| `message` | string | 사람이 읽을 수 있는 처리 결과 메시지 |
| `data` | object, array, null | 실제 응답 데이터 |

## 규칙

- 정상 응답은 `success=true`를 사용한다.
- 정상 응답에서 반환할 데이터가 없으면 빈 객체 `{}` 또는 의미 있는 null 필드를 사용한다.
- 실패 응답은 가능한 한 `success=false`, `data=null` 구조를 사용한다.
- 인증 실패, 요청 검증 실패 등 프레임워크 레벨 오류는 HTTP 상태 코드를 함께 확인한다.

## 예시

### Health

```json
{
  "success": true,
  "message": "서버가 정상적으로 동작 중입니다.",
  "data": {
    "status": "healthy"
  }
}
```

### Status

```json
{
  "success": true,
  "message": "Current status retrieved successfully.",
  "data": {
    "current_state": "EMPTY",
    "last_door_state": null,
    "last_mmwave_detected": false,
    "last_zone": null,
    "last_motion_level": null,
    "last_still_time": null,
    "last_reason": "Initial state",
    "last_updated": null,
    "waiting_for_response": false,
    "pending_response_type": null,
    "abnormal_start_time": null,
    "last_fall_detected": false,
    "last_fall_score": 0.0,
    "last_fall_at": null,
    "active_session": null
  }
}
```

### Calibration Error

캘리브레이션이 활성화되어 있지 않은 상태에서 완료 요청을 보내면 HTTP 400이 반환된다.

```json
{
  "detail": "Calibration is not active."
}
```

### Validation Error

허용되지 않는 값이 들어오면 FastAPI 검증 오류가 반환된다.

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "door_state"],
      "msg": "Input should be 'open' or 'closed'",
      "input": "invalid"
    }
  ]
}
```

## 클라이언트 처리 기준

모바일 앱:

- `success=true`이면 `data`를 화면 상태에 반영한다.
- 네트워크 예외 또는 HTTP 오류는 연결 실패 메시지로 표시한다.
- `data.current_state`는 `EMPTY`, `ENTERING`, `ACTIVE`, `TOILET_USE`, `ABNORMAL`, `EMERGENCY` 중 하나로 해석한다.

IoT 장치:

- 센서 전송 성공 여부는 HTTP 상태 코드와 `success`를 함께 확인한다.
- 서버 연결 실패 시 재시도하거나 로컬 로그를 남긴다.
