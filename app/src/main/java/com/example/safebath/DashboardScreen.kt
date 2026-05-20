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
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.Bathtub
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material3.*
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.ui.unit.dp
import androidx.compose.material.icons.filled.Refresh


// ============================== [3. 대시보드 (하단 탭 뼈대)] ==============================
@Composable
fun UsagePatternDashboard(
    // 💡 1. 기존 x, y 대신 MainActivity가 던져주는 '진짜' 바구니(Map)를 입구에서 받습니다.
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

    // 💡 2. (이전에 이곳에 추가하셨던 임시 savedCoordinates 변수와 LaunchedEffect는 삭제했습니다.)
    // 이제 파라미터로 넘어온 진짜 savedCoordinates를 바로 사용합니다.

    // --- 긴급 알림 팝업 (모든 탭에서 공통 동작) ---
    if (isEmergencyDetected) {
        LaunchedEffect(Unit) {
            playingRingtone = playEmergencyAlarm(context)
            viewModel.updateState(BathState.EMERGENCY) // 상태도 긴급으로 변경
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
                0 -> HomeTabContent(isGuardian, viewModel) { isEmergencyDetected = true }
                1 -> ReportTabContent()
                2 -> SettingsTabContent(
                    savedCoordinates = savedCoordinates,
                    onRecalibrate = onRecalibrate, // ➡️ 공간 재설정 기능 연결
                    onLogout = onLogout            // ➡️ 로그아웃 기능 연결
                )
            }
        }
    }
}

// --- 3-1. 홈 탭 내용 ---
@Composable
fun HomeTabContent(isGuardian: Boolean, viewModel: BathViewModel, onTestEmergency: () -> Unit) {
    val scrollState = rememberScrollState()
    val currentState by viewModel.currentState.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Row(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column {
                if (isGuardian) {
                    Surface(color = Color(0xFFE8F5E9), shape = RoundedCornerShape(16.dp), modifier = Modifier.padding(bottom = 8.dp)) {
                        Text(text = "🛡️ 보호자 모니터링 중",
                            color = Color(0xFF2E7D32),
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                    }
                }
                Text(text = " 안녕하세요,\n ${if(isGuardian) "보호자" else "홍길동"}님! \uD83D\uDC4B", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            }
        }

        // 실시간 상태 반영 카드
        RealTimeStatusCard(state = currentState)

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
                    Text("낙상 센서 테스트 (개발용)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = SafeBathTheme.AlertRed)
                    Text("터치 시 라즈베리파이 낙상 신호를 시뮬레이션합니다.", style = MaterialTheme.typography.bodySmall, color = SafeBathTheme.OnSecondaryText)
                }
            }
        }

        // [테스트 기능] 상태 변경 시뮬레이션 버튼들
        Spacer(modifier = Modifier.height(24.dp))
        Text("상태 변경 시뮬레이터 (개발용)", style = MaterialTheme.typography.labelMedium, color = SafeBathTheme.OnSecondaryText)
        Spacer(modifier = Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { viewModel.updateState(BathState.ENTERING) }, modifier = Modifier.weight(1f)) { Text("진입") }
            Button(onClick = { viewModel.updateState(BathState.ACTIVE) }, modifier = Modifier.weight(1f)) { Text("활동") }
            Button(onClick = { viewModel.updateState(BathState.TOILET_USE) }, modifier = Modifier.weight(1f)) { Text("변기") }
        }
    }
}

// ============================== [탭 2: 리포트 화면 (업그레이드 버전)] ==============================
@Composable
fun ReportTabContent() {
    val scrollState = rememberScrollState()
    val days = listOf("월", "화", "수", "목", "금", "토", "일")
    val nightWeeklyUsage = listOf(1, 2, 0, 1, 3, 2, 1)
    val stayTimeData = listOf(5.5f, 6.0f, 4.5f, 7.0f, 9.5f, 6.5f, 5.0f)

    // 그래프 위에 글씨를 그리기 위한 도구
    val textMeasurer = rememberTextMeasurer()

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(scrollState)) {
        Text("건강 분석 리포트", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 24.dp))

        // --- 1. 주간 종합 안전 지수 ---
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

        // --- 2. 야간 이용 패턴  ---
        Text("야간 화장실 이용 패턴", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth().padding(bottom = 20.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text(text = "요일별 야간 이용", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text(text = "최고 이용일: 금요일", style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText)
                    }
                    //Text(text = "3회", style = MaterialTheme.typography.displayMedium, fontWeight = FontWeight.ExtraBold, color = SafeBathTheme.PrimaryBlue)
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

        // --- 3. 체류 시간 트렌드 ---
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

                    val sidePadding = 40f   // 좌우 여백 (맨 앞/뒤 글씨가 잘리지 않게)
                    val topPadding = 60f    // 위쪽 여백 (글씨가 들어갈 공간)
                    val bottomPadding = 20f // 아래쪽 여백

                    // 전체 도화지 크기에서 여백을 뺀 '실제 그림이 그려질 공간'
                    val drawWidth = size.width - (sidePadding * 2)
                    val drawHeight = size.height - topPadding - bottomPadding

                    val stepX = drawWidth / (stayTimeData.size - 1)
                    val path = Path()

                    // 선 그리기 (계산식에 여백 추가)
                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))

                        if (index == 0) path.moveTo(currentX, currentY) else path.lineTo(currentX, currentY)
                    }
                    drawPath(path = path, color = SafeBathTheme.PrimaryBlue, style = Stroke(width = 6f))

                    // 꼭짓점 원과 숫자 텍스트 그리기
                    stayTimeData.forEachIndexed { index, value ->
                        val currentX = sidePadding + (index * stepX)
                        val currentY = topPadding + (drawHeight - (value / maxTime * drawHeight))

                        // 파란색 원
                        drawCircle(color = SafeBathTheme.PrimaryBlue, radius = 8f, center = Offset(currentX, currentY))

                        // 숫자 텍스트
                        val textStr = "${value}"
                        val textStyle = TextStyle(color = SafeBathTheme.OnSurfaceText, fontSize = 12.sp, fontWeight = FontWeight.Bold)

                        // 💡 글씨의 실제 가로/세로 길이를 측정합니다.
                        val textLayoutResult = textMeasurer.measure(textStr, textStyle)
                        val textWidth = textLayoutResult.size.width
                        val textHeight = textLayoutResult.size.height

                        // 측정한 길이를 바탕으로 원의 정중앙 바로 위에 글씨를 배치합니다.
                        drawText(
                            textLayoutResult = textLayoutResult,
                            topLeft = Offset(currentX - (textWidth / 2f), currentY - textHeight - 15f)
                        )
                    }
                }

                // 하단 요일 텍스트 (위의 sidePadding 비율에 맞게 양끝 여백 조정)
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    days.forEach { Text(text = it, style = MaterialTheme.typography.labelSmall, color = SafeBathTheme.OnSecondaryText) }
                }
            }
        }

        // --- [신규 추가] 4. 최근 특이사항 이력 로그 ---
        Text("최근 특이사항 이력", style = MaterialTheme.typography.titleMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.padding(bottom = 12.dp))
        Card(modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                // 이력 아이템 1
                EventLogItem(time = "어제 03:15 AM", message = "야간 체류 시간 길어짐 (12분)", isWarning = true)
                Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)
                // 이력 아이템 2
                EventLogItem(time = "목요일 01:20 AM", message = "평범한 야간 화장실 이용", isWarning = false)
                Divider(modifier = Modifier.padding(vertical = 12.dp), color = SafeBathTheme.BackgroundGray)
                // 이력 아이템 3
                EventLogItem(time = "수요일 23:45 PM", message = "변기 외 구역 활동 감지 (샤워 추정)", isWarning = false)
            }
        }
        Spacer(modifier = Modifier.height(30.dp))
    }
}

// --- 3-3. 설정 탭 내용 ---
@Composable
fun SettingsTabContent(
    // 💡 x, y 대신 구역별 좌표가 담긴 Map 구조를 통째로 전달받습니다.
    savedCoordinates: Map<CalibrationZone, Pair<Float, Float>>,
    onRecalibrate: () -> Unit,
    onLogout: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text(
            text = "앱 및 기기 설정",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 24.dp)
        )

        // 💡 1. 기기 연동 정보 섹션 카드
        Card(
            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "기기 연동 정보 (mmWave 센서)",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "등록된 구역별 좌표 설정값",
                    style = MaterialTheme.typography.labelMedium,
                    color = SafeBathTheme.OnSecondaryText
                )
                Spacer(modifier = Modifier.height(8.dp))

                // 💡 2. Map에 저장된 구역들을 하나씩 꺼내서 좌표 리스트를 동적으로 렌더링합니다.
                if (savedCoordinates.isEmpty()) {
                    Text(
                        text = "등록된 구역 좌표 정보가 없습니다.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = SafeBathTheme.OnSecondaryText,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                } else {
                    savedCoordinates.forEach { (zone, coord) ->
                        // 구역별 알맞은 아이콘 매핑
                        val icon = when (zone) {
                            CalibrationZone.TOILET -> Icons.Default.EventSeat
                            CalibrationZone.SINK -> Icons.Default.AccessibilityNew
                            CalibrationZone.BATHTUB -> Icons.Default.Bathtub
                        }

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = icon,
                                    contentDescription = null,
                                    tint = SafeBathTheme.PrimaryBlue,
                                    modifier = Modifier.size(20.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                // "(필수)" 텍스트가 노출되지 않도록 깔끔하게 치환
                                Text(
                                    text = zone.title.replace("(필수)", ""),
                                    style = MaterialTheme.typography.bodyLarge,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                            // 소수점 둘째 자리까지 제한해서 출력
                            Text(
                                text = "X: ${String.format("%.2f", coord.first)}m, Y: ${String.format("%.2f", coord.second)}m",
                                style = MaterialTheme.typography.bodyLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        // 💡 [신규 추가] 하단 버튼 2개 세트
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            // 1. 공간 재설정 버튼 (로그인은 유지)
            Button(
                onClick = onRecalibrate,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
                shape = MaterialTheme.shapes.medium
            ) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("전체 공간 재설정 (좌표 다시 찍기)", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            // 2. 로그아웃 버튼 (계정 정보 초기화)
            OutlinedButton(
                onClick = onLogout,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = MaterialTheme.shapes.medium
            ) {
                Icon(Icons.Default.Logout, contentDescription = null, tint = Color.Gray)
                Spacer(modifier = Modifier.width(8.dp))
                Text("로그아웃", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Gray)
            }
        }
    }
}