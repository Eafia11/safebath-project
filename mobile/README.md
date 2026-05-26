# SafeBath Mobile

Android 앱은 SafeBath 백엔드의 상태를 조회하고, 초기 설치 시 욕실 존 캘리브레이션을
수행하는 클라이언트이다.

## 프로젝트 열기

Android Studio에서 `mobile/` 디렉터리를 프로젝트로 연다.

## 주요 패키지

```text
mobile/app/src/main/java/com/example/safebath
```

주요 파일:

- `MainActivity.kt`: 로그인, 캘리브레이션, 대시보드 화면
- `network/SafeBathApiService.kt`: Retrofit API 정의
- `network/SafeBathRepository.kt`: API 호출 래퍼
- `network/NetworkModule.kt`: Retrofit/OkHttp 설정
- `network/ApiModels.kt`: API 요청/응답 DTO

## 백엔드 주소

앱은 `BuildConfig.API_BASE_URL`을 사용한다.

권장 주소:

- Android emulator: `http://10.0.2.2:8000/`
- Physical device: `http://<YOUR_PC_IP>:8000/`

실기기를 사용할 때는 백엔드를 다음처럼 외부 접속 가능하게 실행한다.

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --reload
```

## 연결 API

현재 모바일 앱에서 사용하는 API:

- `GET /health`
- `GET /status`
- `POST /calibration/start`
- `POST /calibration/step`
- `POST /calibration/complete`

## 빌드/테스트

```bash
cd mobile
gradlew.bat test
```

Java 오류가 발생하면 JDK 설치와 `JAVA_HOME` 설정을 확인한다.

## 화면 흐름

```text
LOGIN
  -> CALIBRATION
  -> DASHBOARD
```

대시보드에서는 5초마다 `/status`를 조회하여 현재 욕실 상태를 갱신한다.
