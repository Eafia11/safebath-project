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
    @SerializedName("success") val success: Boolean,
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

data class StatusData(
    @SerializedName("current_state") val currentState: String,
    @SerializedName("last_door_state") val lastDoorState: String?,
    @SerializedName("last_mmwave_detected") val lastMmwaveDetected: Boolean,
    @SerializedName("last_mmwave_seen_at") val lastMmwaveSeenAt: String?,
    @SerializedName("mmwave_online") val mmwaveOnline: Boolean,
    @SerializedName("last_zone") val lastZone: String?,
    @SerializedName("last_motion_level") val lastMotionLevel: Double?,
    @SerializedName("last_still_time") val lastStillTime: Int?,
    @SerializedName("last_reason") val lastReason: String,
    @SerializedName("last_emergency_source") val lastEmergencySource: String?,
    @SerializedName("last_updated") val lastUpdated: String?,
    @SerializedName("waiting_for_response") val waitingForResponse: Boolean,
    @SerializedName("pending_response_type") val pendingResponseType: String?,
    @SerializedName("abnormal_start_time") val abnormalStartTime: String?,
    @SerializedName("last_fall_detected") val lastFallDetected: Boolean,
    @SerializedName("last_fall_score") val lastFallScore: Double,
    @SerializedName("last_fall_at") val lastFallAt: String?
)

data class AlertData(
    @SerializedName("id") val id: Int,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("type") val type: String,
    @SerializedName("level") val level: String,
    @SerializedName("target") val target: String,
    @SerializedName("message") val message: String,
    @SerializedName("status") val status: String
)

data class LatestAlertData(@SerializedName("alert") val alert: AlertData?)

// 4. 구역 설정(캘리브레이션) 요청 데이터
data class CalibrationStartRequest(@SerializedName("user_id") val userId: String)
data class CalibrationCompleteRequest(
    @SerializedName("zone_name") val zoneName: String,
    @SerializedName("center_x") val centerX: Double? = null,
    @SerializedName("center_y") val centerY: Double? = null,
    @SerializedName("radius") val radius: Double? = null,
    @SerializedName("sample_limit") val sampleLimit: Int = 20,
    @SerializedName("min_samples") val minSamples: Int = 5,
    @SerializedName("radius_padding") val radiusPadding: Double = 0.05
)
data class CalibratedZoneData(
    @SerializedName("center_x") val centerX: Double?,
    @SerializedName("center_y") val centerY: Double?,
    @SerializedName("radius") val radius: Double?,
    @SerializedName("calibrated") val calibrated: Boolean
)
data class CalibratedZonesData(
    @SerializedName("toilet") val toilet: CalibratedZoneData?,
    @SerializedName("sink") val sink: CalibratedZoneData?,
    @SerializedName("bath") val bath: CalibratedZoneData?
)
data class ButtonRequest(@SerializedName("button_type") val buttonType: String)

data class WeeklyReportPeriod(
    @SerializedName("start") val start: String,
    @SerializedName("end") val end: String,
    @SerializedName("days") val days: Int
)

data class WeeklyReportSummary(
    @SerializedName("raw_record_count") val rawRecordCount: Int,
    @SerializedName("processed_record_count") val processedRecordCount: Int,
    @SerializedName("detected_count") val detectedCount: Int,
    @SerializedName("anomaly_count") val anomalyCount: Int,
    @SerializedName("fall_count") val fallCount: Int,
    @SerializedName("emergency_count") val emergencyCount: Int,
    @SerializedName("emergency_by_source") val emergencyBySource: Map<String, Int>,
    @SerializedName("night_toilet_count") val nightToiletCount: Int,
    @SerializedName("safety_score") val safetyScore: Int,
    @SerializedName("safety_label") val safetyLabel: String,
    @SerializedName("average_still_time_seconds") val averageStillTimeSeconds: Double,
    @SerializedName("zone_duration_seconds") val zoneDurationSeconds: Map<String, Double>
)

data class WeeklyReportDay(
    @SerializedName("date") val date: String,
    @SerializedName("raw_record_count") val rawRecordCount: Int,
    @SerializedName("detected_count") val detectedCount: Int,
    @SerializedName("anomaly_count") val anomalyCount: Int,
    @SerializedName("fall_count") val fallCount: Int,
    @SerializedName("emergency_count") val emergencyCount: Int,
    @SerializedName("emergency_by_source") val emergencyBySource: Map<String, Int>,
    @SerializedName("night_toilet_count") val nightToiletCount: Int,
    @SerializedName("max_still_time_seconds") val maxStillTimeSeconds: Int,
    @SerializedName("zone_counts") val zoneCounts: Map<String, Int>
)

data class WeeklyReportEvent(
    @SerializedName("timestamp") val timestamp: String?,
    @SerializedName("type") val type: String,
    @SerializedName("level") val level: String,
    @SerializedName("zone") val zone: String,
    @SerializedName("still_time_seconds") val stillTimeSeconds: Int,
    @SerializedName("reason") val reason: String?,
    @SerializedName("source") val source: String?
)

data class WeeklyReportData(
    @SerializedName("period") val period: WeeklyReportPeriod,
    @SerializedName("source") val source: String,
    @SerializedName("summary") val summary: WeeklyReportSummary,
    @SerializedName("daily") val daily: List<WeeklyReportDay>,
    @SerializedName("abnormal_events") val abnormalEvents: List<WeeklyReportEvent>
)

// 5. API 통신 창구 (백엔드 엔드포인트)
interface SafeBathApiService {
    @GET("logs")
    suspend fun getEventLogs(): SafeBathApiResponse<LogDataContainer>

    @GET("anomalies")
    suspend fun getAnomalyStatus(): SafeBathApiResponse<AnomalyData>

    @GET("status")
    suspend fun getStatus(): SafeBathApiResponse<StatusData>

    @GET("alerts/latest")
    suspend fun getLatestAlert(): SafeBathApiResponse<LatestAlertData>

    @POST("calibration/start")
    suspend fun startCalibration(@Body request: CalibrationStartRequest): SafeBathApiResponse<Map<String, Any>>

    @POST("calibration/complete")
    suspend fun completeCalibrationZone(@Body request: CalibrationCompleteRequest): SafeBathApiResponse<Map<String, Any>>

    @GET("calibration/zones")
    suspend fun getCalibratedZones(): SafeBathApiResponse<CalibratedZonesData>

    @GET("reports/weekly")
    suspend fun getWeeklyReport(): SafeBathApiResponse<WeeklyReportData>

    @POST("device/button")
    suspend fun sendButton(@Body request: ButtonRequest): SafeBathApiResponse<Map<String, Any>>
}
