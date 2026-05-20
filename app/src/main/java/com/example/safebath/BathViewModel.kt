// 데이터 관리 로직 (화면의 상태)
package com.example.safebath

import android.content.Context
import android.media.Ringtone
import android.media.RingtoneManager
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

// 긴급 알람 소리 재생 함수
fun playEmergencyAlarm(context: Context): Ringtone? {
    var alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
    if (alarmUri == null) {
        alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
    }
    val ringtone = RingtoneManager.getRingtone(context, alarmUri)
    ringtone?.play()
    return ringtone
}

// 실시간 상태 관리를 위한 ViewModel
class BathViewModel : ViewModel() {
    private val _currentState = MutableStateFlow(BathState.EMPTY)
    val currentState: StateFlow<BathState> = _currentState

    fun updateState(newState: BathState) {      // 현재 상태 함수
        _currentState.value = newState
    }
}

// 특이사항 1건에 대한 데이터 구조
data class BathEventLog(
    val time: String,
    val message: String,
    val isWarning: Boolean
)

// 💡 화면 상태를 관리하는 Enum (기존에 정의하셨던 것)
enum class SafeBathScreen { LOGIN, CALIBRATION, DASHBOARD }
