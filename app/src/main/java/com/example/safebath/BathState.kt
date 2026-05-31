// 모델 및 상태 정의 클래스
package com.example.safebath

import androidx.compose.ui.graphics.Color
// 💡 [백엔드 통신용 데이터 모델 및 API 인터페이스]
import com.google.gson.annotations.SerializedName
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

// UI 테마 컬러 정의
object SafeBathTheme {
    val PrimaryBlue = Color(0xFF2196F3)
    val BackgroundGray = Color(0xFFF2F4F7)
    val OnSurfaceText = Color(0xFF111827)
    val OnSecondaryText = Color(0xFF6B7280)
    val CardBackground = Color.White
    val AlertRed = Color(0xFFE53935)
}

// 욕실 내부 실시간 상태 정의 (mmWave 연동용)
enum class BathState(val description: String, val color: Color) {
    EMPTY("사용 안 함", Color.Gray),
    ENTERING("진입 중", Color(0xFF2196F3)),
    ACTIVE("활동 중", Color(0xFF4CAF50)),
    TOILET_USE("변기 이용 중", Color(0xFF00ACC1)),
    ABNORMAL("이상 행동 감지", Color(0xFFFF9800)),
    EMERGENCY("긴급 상황!", Color(0xFFE53935))
}

// 1. 공통 응답 껍데기
data class SafeBathApiResponse<T>(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String,
    @SerializedName("data") val data: T
)

// 2. 로그 데이터
data class LogDataContainer(@SerializedName("logs") val logs: List<BathEventLog>)

// 3. 이상 상태 데이터
data class AnomalyData(
    @SerializedName("detected") val detected: Boolean,
    @SerializedName("current_state") val currentState: String,
    @SerializedName("current_zone") val currentZone: String?,
    @SerializedName("fall_detected") val fallDetected: Boolean,
    @SerializedName("waiting_for_response") val waitingForResponse: Boolean
)

// 4. 구역 설정(캘리브레이션) 요청 데이터
data class CalibrationStartRequest(@SerializedName("user_id") val userId: String)
data class CalibrationCompleteRequest(
    @SerializedName("zone_name") val zoneName: String,
    @SerializedName("center_x") val centerX: Double,
    @SerializedName("center_y") val centerY: Double,
    @SerializedName("radius") val radius: Double
)

// 5. API 통신 창구 (백엔드 엔드포인트)
interface SafeBathApiService {
    @GET("logs")
    suspend fun getEventLogs(): SafeBathApiResponse<LogDataContainer>

    @GET("anomalies")
    suspend fun getAnomalyStatus(): SafeBathApiResponse<AnomalyData>

    @POST("calibration/start")
    suspend fun startCalibration(@Body request: CalibrationStartRequest): SafeBathApiResponse<Map<String, Any>>

    @POST("calibration/complete")
    suspend fun completeCalibrationZone(@Body request: CalibrationCompleteRequest): SafeBathApiResponse<Map<String, Any>>
}