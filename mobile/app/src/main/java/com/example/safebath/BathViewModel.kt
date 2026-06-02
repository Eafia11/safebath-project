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

fun playEmergencyAlarm(context: Context): Ringtone? {
    var alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
    if (alarmUri == null) {
        alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
    }
    val ringtone = RingtoneManager.getRingtone(context, alarmUri)
    ringtone?.play()
    return ringtone
}

enum class SafeBathScreen { LOGIN, CALIBRATION, DASHBOARD }

data class BathEventLog(
    @SerializedName("timestamp") val time: String,
    @SerializedName("message") val message: String,
    @SerializedName("is_warning") val isWarning: Boolean
)

class BathViewModel : ViewModel() {
    companion object {
        private const val BASE_URL = "http://43.201.28.192:8000/"
    }

    private val _currentState = MutableStateFlow(BathState.EMPTY)
    val currentState: StateFlow<BathState> = _currentState.asStateFlow()

    private val _eventLogs = MutableStateFlow<List<BathEventLog>>(emptyList())
    val eventLogs: StateFlow<List<BathEventLog>> = _eventLogs.asStateFlow()

    private val _anomalyState = MutableStateFlow<AnomalyData?>(null)
    val anomalyState: StateFlow<AnomalyData?> = _anomalyState.asStateFlow()

    private val _statusState = MutableStateFlow<StatusData?>(null)
    val statusState: StateFlow<StatusData?> = _statusState.asStateFlow()

    private val _latestAlert = MutableStateFlow<AlertData?>(null)
    val latestAlert: StateFlow<AlertData?> = _latestAlert.asStateFlow()

    private val _calibratedZones = MutableStateFlow<CalibratedZonesData?>(null)
    val calibratedZones: StateFlow<CalibratedZonesData?> = _calibratedZones.asStateFlow()

    private val _weeklyReport = MutableStateFlow<WeeklyReportData?>(null)
    val weeklyReport: StateFlow<WeeklyReportData?> = _weeklyReport.asStateFlow()

    private val _serverConnected = MutableStateFlow(false)
    val serverConnected: StateFlow<Boolean> = _serverConnected.asStateFlow()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    private val apiService = retrofit.create(SafeBathApiService::class.java)

    init {
        fetchCalibratedZones()
        fetchDashboardLogs()
        fetchWeeklyReport()
        startRealtimeMonitoring()
    }

    fun updateState(newState: BathState) {
        _currentState.value = newState
    }

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

    private fun startRealtimeMonitoring() {
        viewModelScope.launch {
            while (true) {
                refreshRealtimeState()
                delay(3000)
            }
        }
    }

    private suspend fun refreshRealtimeState() {
        try {
            val statusResponse = apiService.getStatus()
            _statusState.value = statusResponse.data
            applyServerState(statusResponse.data.currentState)
            _serverConnected.value = true

            runCatching { apiService.getAnomalyStatus() }
                .onSuccess { _anomalyState.value = it.data }
                .onFailure { it.printStackTrace() }

            runCatching { apiService.getLatestAlert() }
                .onSuccess { _latestAlert.value = it.data.alert }
                .onFailure { it.printStackTrace() }

            runCatching { apiService.getWeeklyReport() }
                .onSuccess { _weeklyReport.value = it.data }
                .onFailure { it.printStackTrace() }
        } catch (e: Exception) {
            _serverConnected.value = false
            e.printStackTrace()
        }
    }

    fun fetchWeeklyReport() {
        viewModelScope.launch {
            try {
                val response = apiService.getWeeklyReport()
                _weeklyReport.value = response.data
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun refreshBackendConnection() {
        viewModelScope.launch {
            refreshRealtimeState()
        }
    }

    fun startCalibrationSession() {
        viewModelScope.launch {
            try {
                apiService.startCalibration(CalibrationStartRequest(userId = "admin"))
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun fetchCalibratedZones() {
        viewModelScope.launch {
            try {
                val response = apiService.getCalibratedZones()
                _calibratedZones.value = response.data
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun sendZoneCoordinate(zoneName: String, x: Float? = null, y: Float? = null, radius: Double? = null) {
        viewModelScope.launch {
            try {
                val request = CalibrationCompleteRequest(
                    zoneName = zoneName,
                    centerX = x?.toDouble(),
                    centerY = y?.toDouble(),
                    radius = radius,
                )
                apiService.completeCalibrationZone(request)
                fetchCalibratedZones()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun confirmSafe() {
        sendButton("confirm_safe")
    }

    fun requestEmergencyCall() {
        sendButton("emergency_call")
    }

    private fun sendButton(buttonType: String) {
        viewModelScope.launch {
            try {
                apiService.sendButton(ButtonRequest(buttonType))
                refreshRealtimeState()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun applyServerState(stateName: String) {
        val mappedState = runCatching { BathState.valueOf(stateName) }.getOrNull() ?: return
        updateState(mappedState)
    }
}
