// 대시보드 화면

package com.example.safebath

import android.media.Ringtone
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Sensors
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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
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
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.Bathtub
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.OutlinedButton

// ============================== [3. 대시보드 (하단 탭 뼈대)] ==============================
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

    // 💡 [통합 포인트 1] 서버의 실시간 이상 징후를 감시합니다!
    val anomalyInfo by viewModel.anomalyState.collectAsState()

    // 서버에서 'detected = true' 또는 'fall_detected = true' 신호가 오면 자동으로 팝업 띄우기
    LaunchedEffect(anomalyInfo) {
        if (anomalyInfo?.detected == true || anomalyInfo?.fallDetected == true) {
            isEmergencyDetected = true
        }
    }

    // --- 긴급 알림 팝업 (모든 탭에서 공통 동작) ---
    if (isEmergencyDetected) {
        LaunchedEffect(Unit) {
            playingRingtone = playEmergencyAlarm(context)
            viewModel.updateState(BathState.EMERGENCY)
        }
        AlertDialog(
            onDismissRequest = { },
            icon = { Icon(Icons.Default.Warning, contentDescription = null, tint = SafeBathTheme.AlertRed, modifier = Modifier.size(48.dp)) },
            title = { Text(text = "낙상 의심 감지!", fontWeight = FontWeight.Bold, color = SafeBathTheme.AlertRed, textAlign = TextAlign.Center) },
            text = { Text("욕실 내에서 쓰러짐 또는 비정상적인 체류가 감지되었습니다.\n\n즉시 확인이 필요합니다!", textAlign = TextAlign.Center) },
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
                    viewModel.updateState(BathState.EMPTY) // 초기화
                }, modifier = Modifier.fillMaxWidth()) {
                    Text("오작동 / 상황 종료", color = SafeBathTheme.OnSecondaryText)
                }
            },
            containerColor = Color.White
        )
    }

    // --- Scaffold 뼈대 및 하단 네비게이션 ---
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
                0 -> HomeTabContent(isGuardian, viewModel)
                // 💡 [통합 포인트 2] 리포트 탭에 진짜 데이터를 넘겨주기 위해 viewModel 전달
                1 -> ReportTabContent(viewModel = viewModel)
                2 -> SettingsTabContent(savedCoordinates, onRecalibrate, onLogout)
            }
        }
    }
}


// --- 3-1. 홈 탭 내용 (시뮬레이터 제거 완료 버전) ---
@Composable
fun HomeTabContent(isGuardian: Boolean, viewModel: BathViewModel) {
    val scrollState = rememberScrollState()
    val currentState by viewModel.currentState.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        // 1. 상단 인사말 영역
        Row(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column {
                if (isGuardian) {
                    Surface(color = Color(0xFFE8F5E9), shape = RoundedCornerShape(16.dp), modifier = Modifier.padding(bottom = 8.dp)) {
                        Text("🛡️ 보호자 모니터링 중", color = Color(0xFF2E7D32), style = MaterialTheme.typography.labelSmall, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                    }
                }
                Text(" 안녕하세요,\n ${if(isGuardian) "보호자" else "김갑수"}님! 👋", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            }
        }

        // 2. 실시간 상태 카드 (기존 유지)
        RealTimeStatusCard(state = currentState)

        Spacer(modifier = Modifier.height(24.dp))

        // 3. [신규] 기기 연결 상태 카드 (IoT 프로젝트 어필용!)
        Text("시스템 상태", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 12.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            // mmWave 센서 상태
            Card(modifier = Modifier.weight(1f), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(10.dp).background(Color(0xFF4CAF50), shape = RoundedCornerShape(50))) // 초록색 불빛
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("레이더 센서", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("정상 작동 중", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                }
            }

            // 서버 동기화 상태
            Card(modifier = Modifier.weight(1f), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Refresh, contentDescription = null, tint = SafeBathTheme.PrimaryBlue, modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("서버 동기화", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("실시간 연동 중", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 4. [신규] 오늘의 요약 카드
        Text("오늘의 안전 요약", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 12.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceAround) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("화장실 이용", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("4회", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = SafeBathTheme.PrimaryBlue)
                }
                Divider(modifier = Modifier.height(40.dp).width(1.dp), color = SafeBathTheme.BackgroundGray)
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("평균 체류", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("6분", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                }
                Divider(modifier = Modifier.height(40.dp).width(1.dp), color = SafeBathTheme.BackgroundGray)
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("특이사항", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("없음", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = Color(0xFF4CAF50))
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 5. [신규] 빠른 긴급 호출 버튼
        Button(
            onClick = { /* 시연용이므로 눌렀을 때의 동작은 비워두거나 토스트 메시지 띄우기 */ },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFFF3E0)),
            shape = MaterialTheme.shapes.medium
        ) {
            Icon(Icons.Default.Call, contentDescription = null, tint = Color(0xFFF57C00))
            Spacer(modifier = Modifier.width(8.dp))
            Text("보호자 긴급 호출", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFFF57C00))
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

// ============================== [탭 2: 리포트 화면 (업그레이드 버전)] ==============================
// 💡 [통합 포인트 3] 뷰모델을 받아와 진짜 로그 데이터를 사용합니다.
@Composable
fun ReportTabContent(viewModel: BathViewModel) {
    val scrollState = rememberScrollState()
    val days = listOf("월", "화", "수", "목", "금", "토", "일")
    val nightWeeklyUsage = listOf(1, 2, 0, 1, 3, 2, 1)
    val stayTimeData = listOf(5.5f, 6.0f, 4.5f, 7.0f, 9.5f, 6.5f, 5.0f)
    val textMeasurer = rememberTextMeasurer()

    // 서버의 진짜 로그 데이터 가져오기!
    val serverLogs by viewModel.eventLogs.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text("건강 분석 리포트", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 24.dp))

        // --- 1. 주간 종합 안전 지수 ---
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.PrimaryBlue),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
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

        // --- 2. 야간 이용 패턴 ---
        Text("야간 화장실 이용 패턴", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 20.dp), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text("요일별 야간 이용", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text("최고 이용일: 금요일", style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
                Row(modifier = Modifier.fillMaxWidth().height(140.dp).padding(top = 16.dp), horizontalArrangement = Arrangement.SpaceEvenly, verticalAlignment = Alignment.Bottom) {
                    nightWeeklyUsage.forEachIndexed { index, count ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(count.toString(), style = MaterialTheme.typography.labelSmall)
                            Box(modifier = Modifier.width(20.dp).height((count * 25).dp.coerceAtLeast(4.dp)).background(SafeBathTheme.PrimaryBlue, shape = MaterialTheme.shapes.small))
                            Text(days[index], style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        }

        // --- 3. 체류 시간 트렌드 ---
        Text("체류 시간 트렌드", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("요일별 평균 체류 시간(분)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
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

                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))
                        drawCircle(color = SafeBathTheme.PrimaryBlue, radius = 8f, center = Offset(currentX, currentY))

                        val textLayoutResult = textMeasurer.measure("$value", TextStyle(color = SafeBathTheme.OnSurfaceText, fontSize = 12.sp, fontWeight = FontWeight.Bold))
                        drawText(textLayoutResult = textLayoutResult, topLeft = Offset(currentX - (textLayoutResult.size.width / 2f), currentY - textLayoutResult.size.height - 15f))
                    }
                }

                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    days.forEach { Text(it, style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText) }
                }
            }
        }

        // --- 4. 최근 특이사항 이력 로그 ---
        Text("최근 특이사항 이력", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                // 💡 [통합 포인트 4] 가짜 데이터를 지우고, 서버에서 온 serverLogs 리스트를 반복문으로 그립니다!
                if (serverLogs.isEmpty()) {
                    Text("아직 기록된 특이사항 로그가 없습니다.", color = SafeBathTheme.OnSecondaryText)
                } else {
                    serverLogs.forEachIndexed { index, log ->
                        EventLogItem(
                            time = log.time,       // 백엔드의 timestamp
                            message = log.message, // 백엔드의 message
                            isWarning = log.isWarning // 백엔드의 is_warning
                        )
                        // 마지막 아이템이 아니면 구분선(Divider)을 그려줍니다.
                        if (index < serverLogs.size - 1) {
                            Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(30.dp))
    }
}

// --- 3-3. 설정 탭 내용 ---
@Composable
fun SettingsTabContent(
    savedCoordinates: Map<CalibrationZone, Pair<Float, Float>>,
    onRecalibrate: () -> Unit,
    onLogout: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("앱 및 기기 설정", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 24.dp))

        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("기기 연동 정보 (mmWave 센서)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(16.dp))
                Text("등록된 구역별 좌표 설정값", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
                Spacer(modifier = Modifier.height(8.dp))

                if (savedCoordinates.isEmpty()) {
                    Text("등록된 구역 좌표 정보가 없습니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(vertical = 8.dp))
                } else {
                    savedCoordinates.forEach { (zone, coord) ->
                        val icon = when (zone) {
                            CalibrationZone.TOILET -> Icons.Default.EventSeat
                            CalibrationZone.SINK -> Icons.Default.AccessibilityNew
                            CalibrationZone.BATHTUB -> Icons.Default.Bathtub
                        }

                        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(icon, contentDescription = null, tint = SafeBathTheme.PrimaryBlue, modifier = Modifier.size(20.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(zone.title.replace("(필수)", ""), style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Medium)
                            }
                            Text("X: ${String.format("%.2f", coord.first)}m, Y: ${String.format("%.2f", coord.second)}m", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Button(onClick = onRecalibrate, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue), shape = MaterialTheme.shapes.medium) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("전체 공간 재설정 (좌표 다시 찍기)", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            OutlinedButton(onClick = onLogout, modifier = Modifier.fillMaxWidth().height(56.dp), shape = MaterialTheme.shapes.medium) {
                Icon(Icons.Default.Logout, contentDescription = null, tint = Color.Gray)
                Spacer(modifier = Modifier.width(8.dp))
                Text("로그아웃", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Gray)
            }
        }
    }
}