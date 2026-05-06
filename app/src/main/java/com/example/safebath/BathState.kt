// 모델 및 상태 정의 클래스
package com.example.safebath

import androidx.compose.ui.graphics.Color

// UI 테마 컬러 정의
object SafeBathTheme {
    val PrimaryBlue = Color(0xFF2196F3)
    val BackgroundGray = Color(0xFFF2F4F7)
    val OnSurfaceText = Color(0xFF111827)
    val OnSecondaryText = Color(0xFF6B7280)
    val CardBackground = Color.White
    val AlertRed = Color(0xFFE53935)
}
// 앱 화면 단위 상태
enum class SafeBathScreen { LOGIN, CALIBRATION, DASHBOARD }

// 욕실 내부 실시간 상태 정의 (mmWave 연동용)
enum class BathState(val description: String, val color: Color) {
    EMPTY("사용 안 함", Color.Gray),
    ENTERING("진입 중", Color(0xFF2196F3)),
    ACTIVE("활동 중", Color(0xFF4CAF50)),
    TOILET_USE("변기 이용 중", Color(0xFF00ACC1)),
    ABNORMAL("이상 행동 감지", Color(0xFFFF9800)),
    EMERGENCY("긴급 상황!", Color(0xFFE53935))
}
