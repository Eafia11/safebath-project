package com.example.safebath

import android.media.Ringtone
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun UsagePatternDashboard(
    savedCoordinates: Map<CalibrationZone, Pair<Float, Float>>,
    isGuardian: Boolean,
    viewModel: BathViewModel,
    onRecalibrate: () -> Unit,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    var isEmergencyDetected by remember { mutableStateOf(false) }
    var playingRingtone by remember { mutableStateOf<Ringtone?>(null) }
    var selectedTab by remember { mutableIntStateOf(0) }

    val anomalyInfo by viewModel.anomalyState.collectAsState()
    val statusInfo by viewModel.statusState.collectAsState()
    val latestAlert by viewModel.latestAlert.collectAsState()

    LaunchedEffect(anomalyInfo, statusInfo) {
        isEmergencyDetected =
            anomalyInfo?.fallDetected == true ||
            statusInfo?.waitingForResponse == true ||
            statusInfo?.currentState == "ABNORMAL" ||
            statusInfo?.currentState == "EMERGENCY"
    }

    if (isEmergencyDetected) {
        LaunchedEffect(Unit) {
            playingRingtone = playEmergencyAlarm(context)
            viewModel.updateState(BathState.EMERGENCY)
        }
        AlertDialog(
            onDismissRequest = { },
            icon = { Icon(Icons.Default.Warning, contentDescription = null, tint = SafeBathTheme.AlertRed) },
            title = { Text("이상 상황 감지", fontWeight = FontWeight.Bold, color = SafeBathTheme.AlertRed) },
            text = { Text("욕실 내 낙상 또는 비정상 체류가 감지되었습니다.") },
            confirmButton = {
                Button(
                    onClick = {
                        playingRingtone?.stop()
                        viewModel.requestEmergencyCall()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.AlertRed),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Call, contentDescription = null, tint = Color.White)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("보호자 긴급 호출", color = Color.White, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = {
                        playingRingtone?.stop()
                        isEmergencyDetected = false
                        viewModel.confirmSafe()
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("안전 확인", color = SafeBathTheme.OnSecondaryText)
                }
            },
            containerColor = Color.White
        )
    }

    Scaffold(
        bottomBar = {
            NavigationBar(containerColor = Color.White, tonalElevation = 8.dp) {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, contentDescription = "홈") },
                    label = { Text("홈") },
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = SafeBathTheme.PrimaryBlue,
                        selectedTextColor = SafeBathTheme.PrimaryBlue,
                        indicatorColor = Color(0xFFE3F2FD)
                    )
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.BarChart, contentDescription = "리포트") },
                    label = { Text("리포트") },
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = SafeBathTheme.PrimaryBlue,
                        selectedTextColor = SafeBathTheme.PrimaryBlue,
                        indicatorColor = Color(0xFFE3F2FD)
                    )
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Settings, contentDescription = "설정") },
                    label = { Text("설정") },
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = SafeBathTheme.PrimaryBlue,
                        selectedTextColor = SafeBathTheme.PrimaryBlue,
                        indicatorColor = Color(0xFFE3F2FD)
                    )
                )
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding).fillMaxSize().background(SafeBathTheme.BackgroundGray)) {
            when (selectedTab) {
                0 -> HomeTabContent(isGuardian, viewModel)
                1 -> ReportTabContent(viewModel)
                2 -> SettingsTabContent(savedCoordinates, onRecalibrate, onLogout)
            }
        }
    }
}

@Composable
fun HomeTabContent(isGuardian: Boolean, viewModel: BathViewModel) {
    val scrollState = rememberScrollState()
    val currentState by viewModel.currentState.collectAsState()
    val weeklyReport by viewModel.weeklyReport.collectAsState()
    val serverConnected by viewModel.serverConnected.collectAsState()
    val dataSensorConnected by viewModel.dataSensorConnected.collectAsState()
    val todayReport = weeklyReport?.daily?.lastOrNull()
    val weeklySummary = weeklyReport?.summary
    val todayUsageCount = todayReport?.nightToiletCount ?: 0
    val averageStayMinutes = ((weeklySummary?.averageStillTimeSeconds ?: 0.0) / 60.0).toInt()
    val abnormalCount = (weeklySummary?.anomalyCount ?: 0) + (weeklySummary?.fallCount ?: 0)

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                if (isGuardian) {
                    Surface(
                        color = Color(0xFFE8F5E9),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.padding(bottom = 8.dp)
                    ) {
                        Text(
                            "보호자 모니터링 중",
                            color = Color(0xFF2E7D32),
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
                Text(
                    "안녕하세요,\n${if (isGuardian) "보호자" else "사용자"}님",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        RealTimeStatusCard(state = currentState)
        Spacer(modifier = Modifier.height(24.dp))

        Text("시스템 상태", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(12.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            StatusMiniCard(
                "데이터 센서",
                if (dataSensorConnected) "센서 연결됨" else "센서 미연결",
                if (dataSensorConnected) Color(0xFF2E7D32) else SafeBathTheme.AlertRed,
                onRefresh = { viewModel.refreshBackendConnection() }
            )
            StatusMiniCard(
                "서버 동기화",
                if (serverConnected) "서버 연결됨" else "연결 실패",
                if (serverConnected) Color(0xFF2E7D32) else SafeBathTheme.AlertRed,
                onRefresh = { viewModel.refreshBackendConnection() }
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text("오늘의 안전 요약", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(12.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceAround) {
                SummaryItem("화장실 이용", "${todayUsageCount}회", SafeBathTheme.PrimaryBlue)
                Divider(modifier = Modifier.height(40.dp).width(1.dp), color = SafeBathTheme.BackgroundGray)
                SummaryItem("평균 체류", "${averageStayMinutes}분", SafeBathTheme.OnSurfaceText)
                Divider(modifier = Modifier.height(40.dp).width(1.dp), color = SafeBathTheme.BackgroundGray)
                SummaryItem(
                    "특이사항",
                    if (abnormalCount == 0) "없음" else "${abnormalCount}건",
                    if (abnormalCount == 0) Color(0xFF4CAF50) else SafeBathTheme.AlertRed
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = { viewModel.requestEmergencyCall() },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFFF3E0)),
            shape = MaterialTheme.shapes.medium
        ) {
            Icon(Icons.Default.Call, contentDescription = null, tint = Color(0xFFF57C00))
            Spacer(modifier = Modifier.width(8.dp))
            Text("보호자 긴급 호출", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFFF57C00))
        }
    }
}

@Composable
private fun StatusMiniCard(label: String, value: String, valueColor: Color = SafeBathTheme.OnSurfaceText) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Refresh, contentDescription = null, tint = SafeBathTheme.PrimaryBlue, modifier = Modifier.size(14.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text(label, style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(value, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = valueColor)
        }
    }
}

@Composable
private fun RowScope.StatusMiniCard(
    label: String,
    value: String,
    valueColor: Color = SafeBathTheme.OnSurfaceText,
    onRefresh: (() -> Unit)? = null
) {
    Card(
        modifier = Modifier.weight(1f),
        colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    label,
                    style = MaterialTheme.typography.labelMedium,
                    color = SafeBathTheme.OnSecondaryText,
                    modifier = Modifier.weight(1f)
                )
                if (onRefresh != null) {
                    IconButton(onClick = onRefresh, modifier = Modifier.size(28.dp)) {
                        Icon(
                            Icons.Default.Refresh,
                            contentDescription = "새로고침",
                            tint = SafeBathTheme.PrimaryBlue,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(value, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold, color = valueColor)
        }
    }
}

@Composable
private fun SummaryItem(label: String, value: String, valueColor: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(4.dp))
        Text(value, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = valueColor)
    }
}

@Composable
fun ReportTabContent(viewModel: BathViewModel) {
    val scrollState = rememberScrollState()
    val weeklyReport by viewModel.weeklyReport.collectAsState()
    val dailyReport = weeklyReport?.daily ?: emptyList()
    val days = dailyReport.map { it.date.takeLast(2) }.ifEmpty { listOf("월", "화", "수", "목", "금", "토", "일") }
    val nightWeeklyUsage = dailyReport.map { it.nightToiletCount }.ifEmpty { List(7) { 0 } }
    val stayTimeData = dailyReport.map { it.maxStillTimeSeconds / 60f }.ifEmpty { List(7) { 0f } }
    val summary = weeklyReport?.summary
    val abnormalEvents = weeklyReport?.abnormalEvents.orEmpty().takeLast(10).asReversed()
    val safetyScore = when {
        summary == null -> 0
        summary.emergencyCount > 0 -> 55
        summary.fallCount > 0 -> 65
        summary.anomalyCount > 0 -> 78
        summary.rawRecordCount == 0 -> 0
        else -> 92
    }
    val safetyLabel = when {
        summary == null || summary.rawRecordCount == 0 -> "데이터 대기"
        safetyScore >= 85 -> "안정적"
        safetyScore >= 70 -> "주의"
        else -> "위험"
    }
    val peakDay = dailyReport.maxByOrNull { it.nightToiletCount }?.date ?: "-"
    val textMeasurer = rememberTextMeasurer()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text("건강 분석 리포트", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.PrimaryBlue),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("이번 주 안전 지수", style = MaterialTheme.typography.labelLarge, color = Color.White.copy(alpha = 0.8f))
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(safetyLabel, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color.White)
                }
                Box(contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(
                        progress = { safetyScore / 100f },
                        modifier = Modifier.size(60.dp),
                        color = Color.White,
                        trackColor = Color.White.copy(alpha = 0.3f),
                        strokeWidth = 6.dp
                    )
                    Text("${safetyScore}점", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = Color.White)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text("야간 화장실 이용 패턴", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(12.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("요일별 야간 이용", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text("최고 이용일: $peakDay", style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
                Spacer(modifier = Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth().height(140.dp).padding(top = 16.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.Bottom
                ) {
                    nightWeeklyUsage.forEachIndexed { index, count ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(count.toString(), style = MaterialTheme.typography.labelSmall)
                            Box(
                                modifier = Modifier.width(20.dp)
                                    .height((count * 25).dp.coerceAtLeast(4.dp))
                                    .background(SafeBathTheme.PrimaryBlue, shape = MaterialTheme.shapes.small)
                            )
                            Text(days.getOrElse(index) { "-" }, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))
        Text("체류 시간 트렌드", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(12.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("요일별 최대 체류 시간(분)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Canvas(modifier = Modifier.fillMaxWidth().height(150.dp).padding(vertical = 16.dp)) {
                    val maxTime = (stayTimeData.maxOrNull() ?: 1f).coerceAtLeast(1f)
                    val sidePadding = 40f
                    val topPadding = 60f
                    val bottomPadding = 20f
                    val drawWidth = size.width - (sidePadding * 2)
                    val drawHeight = size.height - topPadding - bottomPadding
                    val stepX = if (stayTimeData.size > 1) drawWidth / (stayTimeData.size - 1) else 0f
                    val path = Path()

                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))
                        if (index == 0) path.moveTo(currentX, currentY) else path.lineTo(currentX, currentY)
                    }
                    drawPath(path = path, color = SafeBathTheme.PrimaryBlue, style = Stroke(width = 6f))

                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))
                        drawCircle(color = SafeBathTheme.PrimaryBlue, radius = 8f, center = Offset(currentX, currentY))
                        val textLayoutResult = textMeasurer.measure(
                            value.toInt().toString(),
                            TextStyle(color = SafeBathTheme.OnSurfaceText, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        )
                        drawText(
                            textLayoutResult = textLayoutResult,
                            topLeft = Offset(currentX - (textLayoutResult.size.width / 2f), currentY - textLayoutResult.size.height - 15f)
                        )
                    }
                }
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    days.forEach { Text(it, style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText) }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text("최근 특이사항 이력", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(12.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.padding(16.dp)) {
                if (abnormalEvents.isEmpty()) {
                    Text("최근 특이사항이 없습니다.", color = SafeBathTheme.OnSecondaryText)
                } else {
                    abnormalEvents.forEachIndexed { index, event ->
                        EventLogItem(
                            time = event.timestamp ?: "-",
                            message = reportEventMessage(event),
                            isWarning = event.level == "danger"
                        )
                        if (index < abnormalEvents.size - 1) {
                            Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(30.dp))
    }
}

private fun reportEventMessage(event: WeeklyReportEvent): String {
    val typeLabel = when (event.type) {
        "fall" -> "낙상 의심"
        "anomaly" -> "이상 패턴"
        else -> event.type
    }
    val zoneLabel = when (event.zone) {
        "toilet" -> "변기"
        "sink" -> "세면대"
        "bath" -> "욕조"
        "unknown" -> "미분류"
        else -> event.zone
    }
    val stayMinutes = event.stillTimeSeconds / 60
    val reason = event.reason?.let { " · $it" } ?: ""
    return "$typeLabel · $zoneLabel · ${stayMinutes}분 체류$reason"
}

@Composable
fun SettingsTabContent(
    savedCoordinates: Map<CalibrationZone, Pair<Float, Float>>,
    onRecalibrate: () -> Unit,
    onLogout: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("앱 및 기기 설정", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(24.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("등록된 구역 좌표", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(12.dp))
                if (savedCoordinates.isEmpty()) {
                    Text("등록된 구역 좌표 정보가 없습니다.", color = SafeBathTheme.OnSecondaryText)
                } else {
                    savedCoordinates.forEach { (zone, coord) ->
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(zone.title.replace("(필수)", ""))
                            Text("X: ${String.format("%.2f", coord.first)}m, Y: ${String.format("%.2f", coord.second)}m")
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        Button(
            onClick = onRecalibrate,
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue)
        ) {
            Text("전체 공간 재설정", fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }
        Spacer(modifier = Modifier.height(12.dp))
        OutlinedButton(onClick = onLogout, modifier = Modifier.fillMaxWidth().height(56.dp)) {
            Text("로그아웃", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Gray)
        }
    }
}
