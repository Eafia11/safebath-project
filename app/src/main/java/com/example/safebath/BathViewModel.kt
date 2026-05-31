package com.example.safebath

import android.content.Context
import android.media.Ringtone
import android.media.RingtoneManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import kotlinx.coroutines.delay

fun playEmergencyAlarm(context: Context): Ringtone? {
    var alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
    if (alarmUri == null) {
        alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
    }
    val ringtone = RingtoneManager.getRingtone(context, alarmUri)
    ringtone?.play()
    return ringtone
}

// 화면 상태 열거형
enum class SafeBathScreen { LOGIN, CALIBRATION, DASHBOARD }

// 서버에서 받아올 로그 데이터 포맷
data class BathEventLog(
    @SerializedName("timestamp") val time: String,
    @SerializedName("message") val message: String,
    @SerializedName("is_warning") val isWarning: Boolean
)

class BathViewModel : ViewModel() {
    private val _currentState = MutableStateFlow(BathState.EMPTY)
    val currentState: StateFlow<BathState> = _currentState.asStateFlow()

    // 💡 [신규] 서버에서 받아올 진짜 로그 리스트와 실시간 이상 감지 상태
    private val _eventLogs = MutableStateFlow<List<BathEventLog>>(emptyList())
    val eventLogs: StateFlow<List<BathEventLog>> = _eventLogs.asStateFlow()

    private val _anomalyState = MutableStateFlow<AnomalyData?>(null)
    val anomalyState: StateFlow<AnomalyData?> = _anomalyState.asStateFlow()

    // 💡 [신규] 통신 클라이언트 세팅 (IP 주소를 꼭! 수정하세요)
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://본인의_서버IP:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    // 💡 1. 진짜 서버 통신 코드는 잠시 주석(//) 처리해 둡니다.
    // private val apiService = retrofit.create(SafeBathApiService::class.java)

    // 💡 2. 대신 우리가 만든 '가짜 서버'를 연결합니다!
    private val apiService: SafeBathApiService = FakeSafeBathApiService()

    init {
        fetchDashboardLogs()
        startRealtimeMonitoring()
    }

    fun updateState(newState: BathState) {
        _currentState.value = newState
    }

    // 1. 서버에서 로그 가져오기
    fun fetchDashboardLogs() {
        viewModelScope.launch {
            try {
                val response = apiService.getEventLogs()
                _eventLogs.value = response.data.logs
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    // 2. 3초마다 이상 징후 체크하기
    private fun startRealtimeMonitoring() {
        viewModelScope.launch {
            while (true) {
                try {
                    val response = apiService.getAnomalyStatus()
                    _anomalyState.value = response.data

                    // 위험 감지 시 상태 변경 로직 추가 가능
                    if (response.data.detected) updateState(BathState.ABNORMAL)
                } catch (e: Exception) {
                    e.printStackTrace()
                }
                delay(3000)
            }
        }
    }

    // 3. 설정된 구역 좌표 서버로 전송하기
    fun sendZoneCoordinate(zoneName: String, x: Float, y: Float, radius: Double = 1.0) {
        viewModelScope.launch {
            try {
                apiService.startCalibration(CalibrationStartRequest(userId = "admin"))
                val request = CalibrationCompleteRequest(
                    zoneName = zoneName, centerX = x.toDouble(), centerY = y.toDouble(), radius = radius
                )
                apiService.completeCalibrationZone(request)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}

// ==========================================
// 💡 [프론트엔드 단독 테스트용 가짜 서버 대역]
// ==========================================

class FakeSafeBathApiService : SafeBathApiService {

    override suspend fun getEventLogs(): SafeBathApiResponse<LogDataContainer> {
        delay(500) // 0.5초 통신하는 척 딜레이
        return SafeBathApiResponse(
            status = "success",
            message = "더미 로그 조회 성공",
            data = LogDataContainer(
                logs = listOf(
                    BathEventLog("오늘 08:30 AM", "아침 세면대 이용 완료", false),
                    BathEventLog("어제 03:15 AM", "야간 화장실 체류 시간 지연 경고", true),
                    BathEventLog("어제 22:10 PM", "샤워(욕조) 구역 활동 감지", false)
                )
            )
        )
    }

    override suspend fun getAnomalyStatus(): SafeBathApiResponse<AnomalyData> {
        delay(500)
        // 평소에는 안전한 상태를 리턴합니다.
        // (만약 긴급 팝업이 뜨는지 보고 싶다면 detected = true 로 바꿔서 앱을 실행해 보세요!)
        return SafeBathApiResponse(
            status = "success",
            message = "더미 이상 징후 조회 성공",
            data = AnomalyData(
                detected = false,
                currentState = "ACTIVE",
                currentZone = "toilet",
                fallDetected = false,
                waitingForResponse = false
            )
        )
    }

    override suspend fun startCalibration(request: CalibrationStartRequest): SafeBathApiResponse<Map<String, Any>> {
        delay(500)
        return SafeBathApiResponse("success", "가짜 캘리브레이션 시작", emptyMap())
    }

    override suspend fun completeCalibrationZone(request: CalibrationCompleteRequest): SafeBathApiResponse<Map<String, Any>> {
        delay(500)
        return SafeBathApiResponse("success", "${request.zoneName} 가짜 좌표 저장 완료", emptyMap())
    }
}