package com.example.safebath

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext

// (기타 import 문들은 기존과 동일하게 유지해 주세요)

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

    // 실시간 상태 관리를 위한 뷰모델 생성
    val bathViewModel = remember { BathViewModel() }

    var currentScreen by remember { mutableStateOf(SafeBathScreen.LOGIN) }
    var isGuardianMode by remember { mutableStateOf(false) }

    // 💡 [핵심 변경] 단일 x, y 변수를 지우고 Map 상태 변수 하나로 통합!
    val savedCoordinates = remember { mutableStateMapOf<CalibrationZone, Pair<Float, Float>>() }

    // 앱 시작 시 저장된 데이터 불러오기
    LaunchedEffect(Unit) {
        val isLoggedIn = sharedPref.getBoolean("is_logged_in", false)
        isGuardianMode = sharedPref.getBoolean("is_guardian", false)

        if (isLoggedIn) {
            // 💡 [핵심 변경] Enum(변기, 세면대, 욕조)을 돌면서 기기에 저장된 좌표가 있는지 싹 다 꺼내옵니다.
            CalibrationZone.values().forEach { zone ->
                val x = sharedPref.getFloat("coord_${zone.name}_x", -1f)
                val y = sharedPref.getFloat("coord_${zone.name}_y", -1f)
                if (x != -1f && y != -1f) {
                    savedCoordinates[zone] = Pair(x, y) // 불러온 좌표를 맵에 채워넣음
                }
            }

            // 필수 구역인 '변기' 좌표가 Map 안에 무사히 들어있다면 대시보드로 이동
            if (savedCoordinates.containsKey(CalibrationZone.TOILET)) {
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

                SafeBathScreen.CALIBRATION -> ToiletCalibrationScreen(onConfirm = { coordinatesMap ->
                    // 💡 [핵심 변경] 캘리브레이션에서 뭉텅이로 넘어온 Map을 하나씩 쪼개서 기기에 영구 저장
                    with(sharedPref.edit()) {
                        coordinatesMap.forEach { (zone, coord) ->
                            putFloat("coord_${zone.name}_x", coord.first)
                            putFloat("coord_${zone.name}_y", coord.second)
                        }
                        apply()
                    }

                    // 메모리(상태 변수)에도 업데이트
                    savedCoordinates.clear()
                    savedCoordinates.putAll(coordinatesMap)
                    currentScreen = SafeBathScreen.DASHBOARD
                })

                // 대시보드로 x, y 대신 저장된 Map(savedCoordinates)을 통째로 전달
                SafeBathScreen.DASHBOARD -> UsagePatternDashboard(
                    savedCoordinates = savedCoordinates,
                    isGuardian = isGuardianMode,
                    viewModel = bathViewModel,
                    // 동작 1: 재설정 버튼 누름 (좌표만 지우기)
                    onRecalibrate = {
                        with(sharedPref.edit()) {
                            CalibrationZone.values().forEach { zone ->
                                remove("coord_${zone.name}_x")
                                remove("coord_${zone.name}_y")
                            }
                            apply()
                        }
                        savedCoordinates.clear() // 현재 메모리 비우기
                        currentScreen = SafeBathScreen.CALIBRATION // 캘리브레이션(좌표 설정) 화면으로!
                    },

                    // 동작 2: 로그아웃 버튼 누름 (전부 다 지우기)
                    onLogout = {
                        with(sharedPref.edit()) {
                            clear() // 기기에 저장된 계정 정보까지 모조리 폭파!
                            apply()
                        }
                        savedCoordinates.clear()
                        currentScreen = SafeBathScreen.LOGIN // 첫 로그인 화면으로!
                    }
                )
            }
        }
    }
}

