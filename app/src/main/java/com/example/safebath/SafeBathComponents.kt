// 공용 UI 부품 (카드, 버튼 디자인) -> 다른 화면 추가 시 이 파일 오픈

package com.example.safebath

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.DirectionsWalk
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.MeetingRoom
import androidx.compose.material.icons.filled.ReportProblem
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp


// --- 실시간 상태 표시 컴포넌트 ---
@Composable
fun RealTimeStatusCard(state: BathState) {
    // 상태에 따른 픽토그램(아이콘)과 요청하신 상세 문구 매핑
    val (icon, detailText) = when (state) {
        BathState.EMPTY -> Icons.Default.MeetingRoom to "현재 화장실을 이용하는 사람이 없습니다."
        BathState.ENTERING -> Icons.Default.DirectionsWalk to "사용자가 욕실 문을 열고 진입했습니다. \n안전 모니터링을 시작합니다."
        BathState.ACTIVE -> Icons.Default.AccessibilityNew to "사용자가 욕실을 이용 중입니다. \n낙상 위험을 감지합니다."
        BathState.TOILET_USE -> Icons.Default.EventSeat to "사용자가 변기를 이용 중입니다. \n활동 패턴을 분석합니다."
        BathState.ABNORMAL -> Icons.Default.ReportProblem to "비정상적인 체류 시간이 감지되었습니다. \n확인이 필요합니다."
        BathState.EMERGENCY -> Icons.Default.Warning to "낙상 긴급 상황! 119 신고 및 보호자 알람 발송 중"
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = state.color.copy(alpha = 0.1f)),
        border = BorderStroke(2.dp, state.color),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            // 픽토그램 (기존보다 크기를 48.dp로 살짝 키워서 눈에 잘 띄게 함)
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

                // 요청하신 상세 문구를 작게(bodySmall) 하단에 배치
                Text(
                    text = detailText,
                    style = MaterialTheme.typography.bodySmall,
                    color = SafeBathTheme.OnSurfaceText,
                    lineHeight = 16.sp // 글씨가 길어져 두 줄이 될 경우를 위해 줄간격 조정
                )
            }
        }
    }
}

// 이벤트 로그 리스트를 예쁘게 그려주는 미니 컴포넌트
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

// --- 공용 버튼 컴포넌트 ---
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