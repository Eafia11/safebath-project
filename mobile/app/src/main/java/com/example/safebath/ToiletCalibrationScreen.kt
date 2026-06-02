package com.example.safebath

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.Bathtub
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// 1. 구역 정보를 정의하는 Enum (다른 파일에서 써야 한다면 밖으로 빼셔도 됩니다)
enum class CalibrationZone(val title: String, val defaultText: String) {
    TOILET("변기(필수)", "변기에 앉아 아래 버튼을 눌러주세요.\nmmWave 레이더가 현재 좌표를 변기 구역으로 저장합니다."),
    SINK("세면대", "세면대 앞에 서서 아래 버튼을 눌러주세요.\nmmWave 레이더가 현재 좌표를 세면대 구역으로 저장합니다."),
    BATHTUB("욕조", "욕조(또는 샤워기) 부근에 서서 아래 버튼을 눌러주세요.\nmmWave 레이더가 현재 좌표를 욕조 구역으로 저장합니다.")
}

// 2. 메인 화면으로 'Map' 전체를 넘겨주도록 수정된 함수 규격
@Composable
fun ToiletCalibrationScreen(
    viewModel: BathViewModel,  // 💡 [추가] 뷰모델을 받아오도록 입구 열어주기!
    onConfirm: (Map<CalibrationZone, Pair<Float, Float>>) -> Unit
) {
    // --- 상태(State) 관리 ---
    var isSetupMode by remember { mutableStateOf(false) } // false: 선택 화면, true: 측정 화면

    // 체크박스 상태 (변기는 무조건 true)
    var toiletSelected by remember { mutableStateOf(true) }
    var sinkSelected by remember { mutableStateOf(false) }
    var bathtubSelected by remember { mutableStateOf(false) }

    // 사용자가 선택한 구역들만 모아두는 리스트
    val activeZones = remember(isSetupMode) {
        mutableListOf<CalibrationZone>().apply {
            if (toiletSelected) add(CalibrationZone.TOILET)
            if (sinkSelected) add(CalibrationZone.SINK)
            if (bathtubSelected) add(CalibrationZone.BATHTUB)
        }
    }

    var currentStepIndex by remember { mutableStateOf(0) }

    // 💡 [핵심] 측정된 좌표들을 임시로 모아둘 장바구니(Map)
    val savedCoordinates = remember { mutableStateMapOf<CalibrationZone, Pair<Float, Float>>() }
    val serverZones by viewModel.calibratedZones.collectAsState()
    var showUseSavedDialog by remember { mutableStateOf(false) }
    var hasAskedSavedDialog by remember { mutableStateOf(false) }
    val serverCoordinates = remember(serverZones) {
        buildMap {
            serverZones?.toilet?.toPair()?.let { put(CalibrationZone.TOILET, it) }
            serverZones?.sink?.toPair()?.let { put(CalibrationZone.SINK, it) }
            serverZones?.bath?.toPair()?.let { put(CalibrationZone.BATHTUB, it) }
        }
    }

    LaunchedEffect(serverCoordinates, isSetupMode) {
        if (!isSetupMode && !hasAskedSavedDialog && serverCoordinates.containsKey(CalibrationZone.TOILET)) {
            showUseSavedDialog = true
            hasAskedSavedDialog = true
        }
    }

    if (showUseSavedDialog) {
        AlertDialog(
            onDismissRequest = { showUseSavedDialog = false },
            title = { Text("기존 공간 설정 사용") },
            text = { Text("서버에 저장된 공간 좌표가 있습니다. 기존 설정을 사용해서 바로 대시보드로 이동할까요?") },
            confirmButton = {
                Button(onClick = {
                    showUseSavedDialog = false
                    onConfirm(serverCoordinates)
                }) {
                    Text("네, 사용할게요")
                }
            },
            dismissButton = {
                TextButton(onClick = { showUseSavedDialog = false }) {
                    Text("다시 설정")
                }
            }
        )
    }

    // --- 화면 A: 체크박스로 설정할 구역 고르기 ---
    if (!isSetupMode) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("공간 선택", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
                Icon(Icons.Default.Settings, contentDescription = null, tint = Color.LightGray)
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("설정할 욕실 내 구역을 모두 선택해주세요.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText, modifier = Modifier.fillMaxWidth())

            Spacer(modifier = Modifier.height(32.dp))

            // 변기 체크박스 (필수)
            Card(modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
                Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.EventSeat, contentDescription = null, tint = SafeBathTheme.PrimaryBlue)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(CalibrationZone.TOILET.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    }
                    Checkbox(checked = toiletSelected, onCheckedChange = null, enabled = false)
                }
            }

            // 세면대 체크박스
            Card(modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp).clickable { sinkSelected = !sinkSelected }, colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
                Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.AccessibilityNew, contentDescription = null, tint = if (sinkSelected) SafeBathTheme.PrimaryBlue else Color.Gray)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(CalibrationZone.SINK.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    }
                    Checkbox(checked = sinkSelected, onCheckedChange = { sinkSelected = it })
                }
            }

            // 욕조 체크박스
            Card(modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp).clickable { bathtubSelected = !bathtubSelected }, colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
                Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Bathtub, contentDescription = null, tint = if (bathtubSelected) SafeBathTheme.PrimaryBlue else Color.Gray)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(CalibrationZone.BATHTUB.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    }
                    Checkbox(checked = bathtubSelected, onCheckedChange = { bathtubSelected = it })
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            Button(
                onClick = {
                    viewModel.startCalibrationSession()
                    isSetupMode = true
                }, // 다음 화면으로 넘어가기
                modifier = Modifier.fillMaxWidth().height(60.dp),
                colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
                shape = MaterialTheme.shapes.medium
            ) {
                Text("선택 완료 및 좌표 설정 시작", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
    // --- 화면 B: 선택된 구역 순서대로 좌표 측정하기 ---
    else {
        val currentZone = activeZones[currentStepIndex]
        val zoneIcon = when (currentZone) {
            CalibrationZone.TOILET -> Icons.Default.EventSeat
            CalibrationZone.SINK -> Icons.Default.AccessibilityNew
            CalibrationZone.BATHTUB -> Icons.Default.Bathtub
        }

        Column(modifier = Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Top) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("위치 등록", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
                Text(
                    text = "${currentStepIndex + 1} / ${activeZones.size} 단계",
                    style = MaterialTheme.typography.titleMedium,
                    color = SafeBathTheme.PrimaryBlue,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(48.dp))

            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground), elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)) {
                Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(imageVector = zoneIcon, contentDescription = null, modifier = Modifier.size(60.dp), tint = SafeBathTheme.PrimaryBlue)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(text = "${currentZone.title.replace("(필수)", "")} 위치 설정", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(text = currentZone.defaultText, style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText, textAlign = TextAlign.Center)
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            Button(
                onClick = {
                    // 1. 센서에서 받아왔다고 가정하는 더미 좌표

                    // 2. 장바구니(Map)에 현재 구역 좌표 담기

                    // 💡 [신규] 백엔드 서버로 실제 좌표 전송!
                    val backendZoneName = when(currentZone) {
                        CalibrationZone.TOILET -> "toilet"
                        CalibrationZone.SINK -> "sink"
                        CalibrationZone.BATHTUB -> "bath"
                    }
                    viewModel.sendZoneCoordinate(backendZoneName)

                    // 3. 다음 단계로 넘어가거나 완료하기
                    if (currentStepIndex < activeZones.size - 1) {
                        currentStepIndex++ // 다음 구역 화면으로 갱신
                    } else {
                        // 💡 [핵심] 마지막 단계라면, 장바구니 전체를 부모에게 던져주고 종료!
                        onConfirm(savedCoordinates)
                    }
                },
                modifier = Modifier.fillMaxWidth().height(60.dp),
                colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
                shape = MaterialTheme.shapes.medium
            ) {
                Icon(Icons.Default.LocationOn, contentDescription = null)
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = if (currentStepIndex == activeZones.size - 1) "전체 설정 완료 및 저장" else "지금 위치를 확정하고 다음으로",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

private fun CalibratedZoneData.toPair(): Pair<Float, Float>? {
    if (!calibrated || centerX == null || centerY == null) return null
    return Pair(centerX.toFloat(), centerY.toFloat())
}
