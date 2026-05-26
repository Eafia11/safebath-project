package com.example.safebath

import android.content.Context
import android.media.Ringtone
import android.media.RingtoneManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.safebath.network.SafeBathRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.TextStyle

// ============================== [Basic App State] ==============================

// 1. Emergency alarm playback helper
fun playEmergencyAlarm(context: Context): Ringtone? {
    var alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
    if (alarmUri == null) {
        alarmUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
    }
    val ringtone = RingtoneManager.getRingtone(context, alarmUri)
    ringtone?.play()
    return ringtone
}

// 2. UI color palette
object SafeBathTheme {
    val PrimaryBlue = Color(0xFF2196F3)
    val BackgroundGray = Color(0xFFF2F4F7)
    val OnSurfaceText = Color(0xFF111827)
    val OnSecondaryText = Color(0xFF6B7280)
    val CardBackground = Color.White
    val AlertRed = Color(0xFFE53935)
}

// 3. Top-level screen state
enum class SafeBathScreen { LOGIN, CALIBRATION, DASHBOARD }

// 4. Real-time bathroom state from mmWave + rules
enum class BathState(val description: String, val color: Color) {
    EMPTY("사용 안 함", Color.Gray),
    ENTERING("진입 중", Color(0xFF2196F3)),
    ACTIVE("활동 중", Color(0xFF4CAF50)),
    TOILET_USE("변기 이용 중", Color(0xFF00ACC1)),
    ABNORMAL("이상 상태 감지", Color(0xFFFF9800)),
    EMERGENCY("긴급 상황", Color(0xFFE53935))
}

data class ZoneCalibrationInput(
    val zoneName: String,
    val displayName: String,
    val x: Float,
    val y: Float,
    val radius: Float,
)

private class ZoneCalibrationDraft(
    val zoneName: String,
    val displayName: String,
    x: String,
    y: String,
    radius: String,
) {
    var x by mutableStateOf(x)
    var y by mutableStateOf(y)
    var radius by mutableStateOf(radius)
}

// 5. ViewModel for real-time state management
class BathViewModel : ViewModel() {
    private val repository = SafeBathRepository()
    private var pollingJob: Job? = null
    private val _currentState = MutableStateFlow(BathState.EMPTY)
    val currentState: StateFlow<BathState> = _currentState
    private val _statusMessage = MutableStateFlow("Waiting for API connection")
    val statusMessage: StateFlow<String> = _statusMessage
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    init {
        refreshStatus()
    }

    fun updateState(newState: BathState) {
        _currentState.value = newState
    }

    fun refreshStatus(showLoading: Boolean = true) {
        viewModelScope.launch {
            if (showLoading) {
                _isLoading.value = true
            }
            runCatching {
                val health = repository.checkHealth()
                val status = repository.getStatus()
                health to status
            }.onSuccess { (health, status) ->
                val stateName = status.data?.current_state.orEmpty()
                _currentState.value = stateName.toBathState()
                _statusMessage.value = if (health.success && status.success) {
                    "서버 연결 정상 · 현재 상태 ${stateName.ifBlank { "UNKNOWN" }}"
                } else {
                    status.message
                }
            }.onFailure { error ->
                _statusMessage.value = "서버 연결 실패: ${error.message ?: "알 수 없는 오류"}"
            }
            if (showLoading) {
                _isLoading.value = false
            }
        }
    }

    fun startStatusPolling(intervalMillis: Long = 5_000L) {
        if (pollingJob?.isActive == true) return

        pollingJob = viewModelScope.launch {
            while (true) {
                refreshStatus(showLoading = false)
                delay(intervalMillis)
            }
        }
    }

    fun stopStatusPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    fun completeBathroomCalibration(
        zones: List<ZoneCalibrationInput>,
        onSuccess: (ZoneCalibrationInput) -> Unit,
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            runCatching {
                repository.startCalibration(userId = "mobile_user")
                zones.forEach { zone ->
                    repository.setCalibrationStep(zoneName = zone.zoneName)
                    repository.completeCalibration(
                        zoneName = zone.zoneName,
                        centerX = zone.x,
                        centerY = zone.y,
                        radius = zone.radius,
                    )
                }
            }.onSuccess {
                _statusMessage.value = "toilet / sink / bath 존 정보가 서버에 저장되었습니다"
                onSuccess(zones.first { it.zoneName == "toilet" })
            }.onFailure { error ->
                _statusMessage.value = "보정 요청 실패: ${error.message ?: "알 수 없는 오류"}"
            }
            _isLoading.value = false
        }
    }
}

private fun String.toBathState(): BathState = when (this.uppercase()) {
    "EMPTY" -> BathState.EMPTY
    "ENTERING" -> BathState.ENTERING
    "ACTIVE" -> BathState.ACTIVE
    "TOILET_USE" -> BathState.TOILET_USE
    "ABNORMAL" -> BathState.ABNORMAL
    "EMERGENCY" -> BathState.EMERGENCY
    else -> BathState.EMPTY
}

// ============================== [Main Entry] ==============================

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { SafeBathApp() }
    }
}

@Composable
fun SafeBathApp() {
    val context = LocalContext.current
    val sharedPref = remember { context.getSharedPreferences("SafeBathPrefs", Context.MODE_PRIVATE) }

    // ViewModel used across the app flow
    val bathViewModel = remember { BathViewModel() }

    var currentScreen by remember { mutableStateOf(SafeBathScreen.LOGIN) }
    var savedX by remember { mutableFloatStateOf(0.0f) }
    var savedY by remember { mutableFloatStateOf(0.0f) }
    var isGuardianMode by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        val isLoggedIn = sharedPref.getBoolean("is_logged_in", false)
        isGuardianMode = sharedPref.getBoolean("is_guardian", false)
        if (isLoggedIn) {
            val x = sharedPref.getFloat("toilet_x", -1f)
            val y = sharedPref.getFloat("toilet_y", -1f)
            if (x != -1f && y != -1f) {
                savedX = x
                savedY = y
                currentScreen = SafeBathScreen.DASHBOARD
            } else {
                currentScreen = SafeBathScreen.CALIBRATION
            }
        } else {
            currentScreen = SafeBathScreen.LOGIN
        }
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = SafeBathTheme.BackgroundGray) {
            when (currentScreen) {
                SafeBathScreen.LOGIN -> LoginScreen(onLoginSuccess = { isGuardian ->
                    with(sharedPref.edit()) {
                        putBoolean("is_logged_in", true)
                        putBoolean("is_guardian", isGuardian)
                        apply()
                    }
                    isGuardianMode = isGuardian
                    currentScreen = if (isGuardian) SafeBathScreen.DASHBOARD else SafeBathScreen.CALIBRATION
                })

                SafeBathScreen.CALIBRATION -> ToiletCalibrationScreen(viewModel = bathViewModel, onConfirm = { toiletZone, allZones ->
                    with(sharedPref.edit()) {
                        putFloat("toilet_x", toiletZone.x)
                        putFloat("toilet_y", toiletZone.y)
                        allZones.forEach { zone ->
                            putFloat("${zone.zoneName}_x", zone.x)
                            putFloat("${zone.zoneName}_y", zone.y)
                            putFloat("${zone.zoneName}_radius", zone.radius)
                        }
                        apply()
                    }
                    savedX = toiletZone.x
                    savedY = toiletZone.y
                    bathViewModel.refreshStatus()
                    currentScreen = SafeBathScreen.DASHBOARD
                })

                SafeBathScreen.DASHBOARD -> UsagePatternDashboard(
                    x = savedX,
                    y = savedY,
                    isGuardian = isGuardianMode,
                    viewModel = bathViewModel,
                    onReset = {
                        with(sharedPref.edit()) {
                            clear()
                            apply()
                        }
                        currentScreen = SafeBathScreen.LOGIN
                    }
                )
            }
        }
    }
}

// ============================== [1. Login Screen] ==============================
@Composable
fun LoginScreen(onLoginSuccess: (Boolean) -> Unit) {
    var isGuardianChecked by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize().padding(30.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(Icons.Default.AccessibilityNew, contentDescription = null, modifier = Modifier.size(70.dp), tint = SafeBathTheme.PrimaryBlue)
        Spacer(modifier = Modifier.height(16.dp))
        Text("SafeBath", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.ExtraBold, color = SafeBathTheme.PrimaryBlue)
        Text("욕실 안전 상태를 확인하는 시작 화면", style = MaterialTheme.typography.bodyLarge, color = SafeBathTheme.OnSecondaryText)

        Spacer(modifier = Modifier.height(40.dp))

        Card(
            modifier = Modifier.fillMaxWidth().clickable { isGuardianChecked = !isGuardianChecked },
            colors = CardDefaults.cardColors(containerColor = if (isGuardianChecked) Color(0xFFE3F2FD) else SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            shape = RoundedCornerShape(12.dp),
        ) {
            Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.HealthAndSafety, contentDescription = null, tint = if (isGuardianChecked) SafeBathTheme.PrimaryBlue else Color.Gray)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text("보호자 모드", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text("원격으로 상태를 확인하는 시연 모드", style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.OnSecondaryText)
                    }
                }
                Switch(checked = isGuardianChecked, onCheckedChange = { isGuardianChecked = it }, colors = SwitchDefaults.colors(checkedThumbColor = SafeBathTheme.PrimaryBlue, checkedTrackColor = Color(0xFFBBDEFB)))
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("현재 앱 상태", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text("이 화면은 실제 계정 인증이 아니라 시연용 시작 화면입니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText)
                Text(if (isGuardianChecked) "선택된 모드: 보호자" else "선택된 모드: 사용자", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSurfaceText)
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { onLoginSuccess(isGuardianChecked) },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
            shape = MaterialTheme.shapes.medium
        ) {
            Text(if (isGuardianChecked) "보호자 모드로 시작" else "사용자 모드로 시작", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}

// ============================== [2. Calibration Screen] ==============================
@Composable
fun ToiletCalibrationScreen(
    viewModel: BathViewModel,
    onConfirm: (ZoneCalibrationInput, List<ZoneCalibrationInput>) -> Unit,
) {
    val isLoading by viewModel.isLoading.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()
    var validationMessage by remember { mutableStateOf<String?>(null) }
    val zoneDrafts = remember { mutableStateListOf<ZoneCalibrationDraft>() }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp).verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Top
    ) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text("보정", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
            Icon(Icons.Default.Settings, contentDescription = null, tint = Color.LightGray)
        }
        Spacer(modifier = Modifier.height(24.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFFE3F2FD)),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("현재 단계", style = MaterialTheme.typography.labelLarge, color = SafeBathTheme.PrimaryBlue)
                Text("욕실 존 위치 보정", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText)
                Text("처음에는 비어 있는 상태로 시작하고, 사용자가 toilet / sink / bath 존을 직접 추가해 저장합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText)
            }
        }
        Spacer(modifier = Modifier.height(20.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.Start, verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Icon(Icons.Default.AccessibilityNew, contentDescription = null, modifier = Modifier.size(60.dp), tint = SafeBathTheme.PrimaryBlue)
                Text("욕실 주요 위치 설정", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText)
                Text("존 추가 버튼을 눌러 주요 위치를 하나씩 등록합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText)
                Text("1. toilet, sink, bath 중 아직 추가되지 않은 존을 생성합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSurfaceText)
                Text("2. 각 존의 중심 좌표와 반경(radius)을 입력합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSurfaceText)
                Text("3. 저장 후 백엔드가 좌표를 존 정보로 사용합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSurfaceText)
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedButton(
            onClick = {
                createNextZoneDraft(zoneDrafts)?.let { zoneDrafts.add(it) }
            },
            enabled = !isLoading && zoneDrafts.size < 3,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Default.Add, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text(if (zoneDrafts.isEmpty()) "존 추가" else "다음 존 추가")
        }
        Spacer(modifier = Modifier.height(12.dp))
        if (zoneDrafts.isEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(Icons.Default.AddLocationAlt, contentDescription = null, tint = SafeBathTheme.PrimaryBlue, modifier = Modifier.size(42.dp))
                    Text("아직 추가된 존이 없습니다.", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text("먼저 존 추가 버튼을 눌러 toilet, sink, bath 중 필요한 위치를 등록해주세요.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText, textAlign = TextAlign.Center)
                }
            }
        } else {
            zoneDrafts.forEachIndexed { index, draft ->
                ZoneCalibrationCard(
                    title = "${draft.zoneName} 존",
                    xValue = draft.x,
                    onXChange = { draft.x = it },
                    yValue = draft.y,
                    onYChange = { draft.y = it },
                    radiusValue = draft.radius,
                    onRadiusChange = { draft.radius = it },
                )
                if (index != zoneDrafts.lastIndex) {
                    Spacer(modifier = Modifier.height(12.dp))
                }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("저장 상태", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                validationMessage?.let {
                    Text(it, style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.AlertRed)
                }
                Text(statusMessage, style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.OnSecondaryText)
            }
        }
        Spacer(modifier = Modifier.weight(1f))
        Button(
            onClick = {
                if (zoneDrafts.isEmpty()) {
                    validationMessage = "최소 1개의 존을 추가해주세요."
                    return@Button
                }

                val zones = zoneDrafts.mapNotNull { draft ->
                    parseZoneCalibration(
                        zoneName = draft.zoneName,
                        displayName = draft.displayName,
                        x = draft.x,
                        y = draft.y,
                        radius = draft.radius,
                    )
                }

                if (zones.size != zoneDrafts.size) {
                    validationMessage = "추가한 모든 존의 x, y, radius를 올바른 숫자로 입력해주세요."
                } else if (zones.none { it.zoneName == "toilet" }) {
                    validationMessage = "대시보드 연결을 위해 toilet 존은 반드시 추가해주세요."
                } else {
                    validationMessage = null
                    val toiletZone = zones.first { it.zoneName == "toilet" }
                    viewModel.completeBathroomCalibration(zones) {
                        onConfirm(toiletZone, zones)
                    }
                }
            },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth().height(60.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
            shape = MaterialTheme.shapes.medium
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(22.dp),
                    color = Color.White,
                    strokeWidth = 2.dp
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text("서버에 저장 중", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            } else {
                Icon(Icons.Default.LocationOn, contentDescription = null)
                Spacer(modifier = Modifier.width(12.dp))
                Text("욕실 존 정보를 서버에 저장", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
        }
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = "보정 완료 후 toilet 존 좌표를 기준으로 대시보드로 이동합니다.",
            style = MaterialTheme.typography.bodySmall,
            color = SafeBathTheme.OnSecondaryText,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
private fun ZoneCalibrationCard(
    title: String,
    xValue: String,
    onXChange: (String) -> Unit,
    yValue: String,
    onYChange: (String) -> Unit,
    radiusValue: String,
    onRadiusChange: (String) -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            OutlinedTextField(
                value = xValue,
                onValueChange = onXChange,
                label = { Text("center_x") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = yValue,
                onValueChange = onYChange,
                label = { Text("center_y") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = radiusValue,
                onValueChange = onRadiusChange,
                label = { Text("radius") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

private fun parseZoneCalibration(
    zoneName: String,
    displayName: String,
    x: String,
    y: String,
    radius: String,
): ZoneCalibrationInput? {
    val parsedX = x.toFloatOrNull() ?: return null
    val parsedY = y.toFloatOrNull() ?: return null
    val parsedRadius = radius.toFloatOrNull() ?: return null
    if (parsedRadius <= 0f) return null
    return ZoneCalibrationInput(
        zoneName = zoneName,
        displayName = displayName,
        x = parsedX,
        y = parsedY,
        radius = parsedRadius,
    )
}

private fun createNextZoneDraft(existingZones: List<ZoneCalibrationDraft>): ZoneCalibrationDraft? {
    val remainingZone = listOf("toilet", "sink", "bath")
        .firstOrNull { candidate -> existingZones.none { it.zoneName == candidate } }
        ?: return null

    return when (remainingZone) {
        "toilet" -> ZoneCalibrationDraft("toilet", "변기", "1.25", "0.78", "0.7")
        "sink" -> ZoneCalibrationDraft("sink", "세면대", "2.10", "0.95", "0.7")
        else -> ZoneCalibrationDraft("bath", "욕조", "1.70", "1.20", "0.7")
    }
}

// ============================== [3. Dashboard] ==============================
@Composable
fun UsagePatternDashboard(x: Float, y: Float, isGuardian: Boolean, viewModel: BathViewModel, onReset: () -> Unit) {
    val context = LocalContext.current
    var isEmergencyDetected by remember { mutableStateOf(false) }
    var playingRingtone by remember { mutableStateOf<Ringtone?>(null) }
    var selectedTab by remember { mutableIntStateOf(0) }

    LaunchedEffect(selectedTab) {
        if (selectedTab == 0) {
            viewModel.startStatusPolling()
        } else {
            viewModel.stopStatusPolling()
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            viewModel.stopStatusPolling()
        }
    }

    // Emergency alert popup shown from any tab
    if (isEmergencyDetected) {
        LaunchedEffect(Unit) {
            playingRingtone = playEmergencyAlarm(context)
            viewModel.updateState(BathState.EMERGENCY)
        }
        AlertDialog(
            onDismissRequest = { },
            icon = { Icon(Icons.Default.Warning, contentDescription = null, tint = SafeBathTheme.AlertRed, modifier = Modifier.size(48.dp)) },
            title = { Text(text = "긴급 상황 감지", fontWeight = FontWeight.Bold, color = SafeBathTheme.AlertRed, textAlign = TextAlign.Center) },
            text = { Text("욕실 내 쓰러짐 또는 비정상 체류가 감지되었습니다.\n\n즉시 확인이 필요합니다.", textAlign = TextAlign.Center) },
            confirmButton = {
                Button(
                    onClick = { playingRingtone?.stop() },
                    colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.AlertRed),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)
                ) {
                    Icon(Icons.Default.Call, contentDescription = null, tint = Color.White)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("119 긴급 신고", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    playingRingtone?.stop()
                    isEmergencyDetected = false
                    viewModel.updateState(BathState.EMPTY)
                }, modifier = Modifier.fillMaxWidth()) {
                    Text("오경보 / 상황 종료", color = SafeBathTheme.OnSecondaryText)
                }
            },
            containerColor = Color.White
        )
    }

    // Scaffold with bottom navigation
    Scaffold(
        bottomBar = {
            NavigationBar(containerColor = Color.White, tonalElevation = 8.dp) {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, contentDescription = "홈") }, label = { Text("홈") },
                    selected = selectedTab == 0, onClick = { selectedTab = 0 },
                    colors = NavigationBarItemDefaults.colors(selectedIconColor = SafeBathTheme.PrimaryBlue, selectedTextColor = SafeBathTheme.PrimaryBlue, indicatorColor = Color(0xFFE3F2FD))
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.BarChart, contentDescription = "리포트") }, label = { Text("리포트") },
                    selected = selectedTab == 1, onClick = { selectedTab = 1 },
                    colors = NavigationBarItemDefaults.colors(selectedIconColor = SafeBathTheme.PrimaryBlue, selectedTextColor = SafeBathTheme.PrimaryBlue, indicatorColor = Color(0xFFE3F2FD))
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Settings, contentDescription = "설정") }, label = { Text("설정") },
                    selected = selectedTab == 2, onClick = { selectedTab = 2 },
                    colors = NavigationBarItemDefaults.colors(selectedIconColor = SafeBathTheme.PrimaryBlue, selectedTextColor = SafeBathTheme.PrimaryBlue, indicatorColor = Color(0xFFE3F2FD))
                )
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding).fillMaxSize().background(SafeBathTheme.BackgroundGray)) {
            when (selectedTab) {
                0 -> HomeTabContent(isGuardian, viewModel) { isEmergencyDetected = true }
                1 -> ReportTabContent()
                2 -> SettingsTabContent(x, y, onReset)
            }
        }
    }
}

// Home tab
@Composable
fun HomeTabContent(isGuardian: Boolean, viewModel: BathViewModel, onTestEmergency: () -> Unit) {
    val scrollState = rememberScrollState()
    val currentState by viewModel.currentState.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Row(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column {
                if (isGuardian) {
                    Surface(color = Color(0xFFE8F5E9), shape = RoundedCornerShape(16.dp), modifier = Modifier.padding(bottom = 8.dp)) {
                        Text(text = "보호자 모니터링 중",
                            color = Color(0xFF2E7D32),
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                    }
                }
                Text(
                    text = "안녕하세요\n${if (isGuardian) "보호자" else "사용자"}님",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        // Real-time state card
        RealTimeStatusCard(state = currentState)
        Spacer(modifier = Modifier.height(12.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("서버 연결 상태", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Text(statusMessage, style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.OnSecondaryText)
                    Text("홈 화면에서 5초마다 자동 갱신됩니다.", style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
                }
                OutlinedButton(onClick = { viewModel.refreshStatus() }, enabled = !isLoading) {
                    Text(if (isLoading) "연결 중" else "새로고침")
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth().clickable { onTestEmergency() },
            colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE)),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Sensors, contentDescription = null, tint = SafeBathTheme.AlertRed)
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text("이상 상황 테스트", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SafeBathTheme.AlertRed)
                    Text("발표 시연용으로 긴급 상태 화면을 바로 확인합니다.", style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.OnSecondaryText)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text("상태 변경 시뮬레이션 (개발용)", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { viewModel.updateState(BathState.ENTERING) }, modifier = Modifier.weight(1f)) { Text("진입") }
            Button(onClick = { viewModel.updateState(BathState.ACTIVE) }, modifier = Modifier.weight(1f)) { Text("활동") }
            Button(onClick = { viewModel.updateState(BathState.TOILET_USE) }, modifier = Modifier.weight(1f)) { Text("변기") }
        }
    }
}

// Real-time status card
@Composable
fun RealTimeStatusCard(state: BathState) {
    val (icon, detailText) = when (state) {
        BathState.EMPTY -> Icons.Default.MeetingRoom to "현재 욕실 사용이 감지되지 않았습니다."
        BathState.ENTERING -> Icons.Default.DirectionsWalk to "사용자가 욕실에 진입한 상태입니다.\n센서 기반 모니터링을 시작합니다."
        BathState.ACTIVE -> Icons.Default.AccessibilityNew to "욕실 사용이 정상적으로 진행 중입니다.\n실시간 상태를 계속 확인합니다."
        BathState.TOILET_USE -> Icons.Default.EventSeat to "변기 사용 패턴이 감지되었습니다.\n체류 시간과 움직임을 분석합니다."
        BathState.ABNORMAL -> Icons.Default.ReportProblem to "평소와 다른 정체 상태가 감지되었습니다.\n보호자 확인이 필요할 수 있습니다."
        BathState.EMERGENCY -> Icons.Default.Warning to "긴급 상황으로 분류되었습니다.\n보호자 알림과 빠른 대응이 필요한 상태입니다."
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = state.color.copy(alpha = 0.1f)),
        border = BorderStroke(2.dp, state.color),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = state.color,
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(text = "현재 욕실 상태", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                Text(text = state.description, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = state.color)

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = detailText,
                    style = MaterialTheme.typography.bodySmall,
                    color = SafeBathTheme.OnSurfaceText,
                    lineHeight = 16.sp
                )
            }
        }
    }
}


@Composable
fun ReportTabContent() {
    val scrollState = rememberScrollState()
    val days = listOf("월", "화", "수", "목", "금", "토", "일")
    val nightWeeklyUsage = listOf(1, 2, 0, 1, 3, 2, 1)
    val stayTimeData = listOf(5.5f, 6.0f, 4.5f, 7.0f, 9.5f, 6.5f, 5.0f)


    val textMeasurer = rememberTextMeasurer()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text("건강 분석 리포트", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 24.dp))


        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.PrimaryBlue),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween)
            {
                Column {
                    Text("이번 주 안전 지수", style = MaterialTheme.typography.labelLarge, color = Color.White.copy(alpha = 0.8f))
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("안정적", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color.White)
                }
                Box(contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(progress = { 0.92f }, modifier = Modifier.size(60.dp), color = Color.White, trackColor = Color.White.copy(alpha = 0.3f), strokeWidth = 6.dp)
                    Text("92점", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = Color.White)
                }
            }
        }


        Text("야간 화장실 이용 패턴", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 20.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text(text = "요일별 야간 이용", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text(text = "최다 이용일: 금요일", style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
                    }
                    //Text(text = "3??, style = MaterialTheme.typography.displayMedium, fontWeight = FontWeight.ExtraBold, color = SafeBathTheme.PrimaryBlue)
                }
                Spacer(modifier = Modifier.height(16.dp))
                Row(modifier = Modifier.fillMaxWidth().height(140.dp).padding(top = 16.dp), horizontalArrangement = Arrangement.SpaceEvenly, verticalAlignment = Alignment.Bottom) {
                    nightWeeklyUsage.forEachIndexed { index, count ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(text = count.toString(), style = MaterialTheme.typography.labelSmall)
                            Box(modifier = Modifier.width(20.dp).height((count * 25).dp.coerceAtLeast(4.dp)).background(SafeBathTheme.PrimaryBlue, shape = MaterialTheme.shapes.small))
                            Text(text = days[index], style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        }


        Text("체류 시간 트렌드", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "요일별 평균 체류 시간(분)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                Canvas(modifier = Modifier.fillMaxWidth().height(150.dp).padding(vertical = 16.dp)) {
                    val maxTime = stayTimeData.maxOrNull() ?: 1f

                    val sidePadding = 40f
                    val topPadding = 60f
                    val bottomPadding = 20f


                    val drawWidth = size.width - (sidePadding * 2)
                    val drawHeight = size.height - topPadding - bottomPadding

                    val stepX = drawWidth / (stayTimeData.size - 1)
                    val path = Path()


                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))

                        if (index == 0) path.moveTo(currentX, currentY) else path.lineTo(currentX, currentY)
                    }
                    drawPath(path = path, color = SafeBathTheme.PrimaryBlue, style = Stroke(width = 6f))

                    // 瑗?쭞???먭낵 ?レ옄 ?띿뒪??洹몃━湲?
                        stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))

                        drawCircle(color = SafeBathTheme.PrimaryBlue, radius = 8f, center = Offset(currentX, currentY))

                        val textStr = "${value}"
                        val textStyle = TextStyle(color = SafeBathTheme.OnSurfaceText, fontSize = 12.sp, fontWeight = FontWeight.Bold)


                        val textLayoutResult = textMeasurer.measure(textStr, textStyle)
                        val textWidth = textLayoutResult.size.width
                        val textHeight = textLayoutResult.size.height

                        drawText(
                            textLayoutResult = textLayoutResult,
                            topLeft = Offset(currentX - (textWidth / 2f), currentY - textHeight - 15f)
                        )
                    }
                }


                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    days.forEach { Text(text = it, style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText) }
                }
            }
        }


        Text("최근 특이사항 이력", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {

                EventLogItem(time = "어제 03:15 AM", message = "야간 체류 시간이 길어짐 (12분)", isWarning = true)
                Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)

                EventLogItem(time = "목요일 01:20 AM", message = "평소보다 야간 화장실 이용 증가", isWarning = false)
                Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)

                EventLogItem(time = "수요일 23:45 PM", message = "변기 구역 체류 감지 (샤워 후 추정)", isWarning = false)
            }
        }
        Spacer(modifier = Modifier.height(30.dp))
    }
}


@Composable
fun EventLogItem(time: String, message: String, isWarning: Boolean) {
    Row(verticalAlignment = Alignment.Top, modifier = Modifier.fillMaxWidth()) {
        Icon(
            imageVector = if (isWarning) Icons.Default.Warning else Icons.Default.Info,
            contentDescription = null,
            tint = if (isWarning) SafeBathTheme.AlertRed else SafeBathTheme.PrimaryBlue,
            modifier = Modifier.size(20.dp).padding(top = 2.dp)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Text(text = message, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText)
            Text(text = time, style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
        }
    }
}

// Settings tab
@Composable
fun SettingsTabContent(x: Float, y: Float, onReset: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("앱 및 기기 설정", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 24.dp))

        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("기기 연동 정보", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("현재 변기 좌표 설정값", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                Text("X: ${x}m,  Y: ${y}m", style = MaterialTheme.typography.bodyLarge)
            }
        }

        PrimaryActionButton(label = "전체 초기화 (로그아웃)", icon = Icons.Default.Logout, onClick = onReset, modifier = Modifier.fillMaxWidth(0.5f))
    }
}


@Composable
fun PrimaryActionButton(label: String, icon: ImageVector, onClick: () -> Unit, modifier: Modifier) {
    Card(
        modifier = modifier.clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Icon(icon, contentDescription = null, modifier = Modifier.size(32.dp), tint = SafeBathTheme.PrimaryBlue)
            Spacer(modifier = Modifier.height(12.dp))
            Text(text = label, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText, textAlign = TextAlign.Center)
        }
    }
}
