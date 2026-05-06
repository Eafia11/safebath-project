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
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.TextStyle

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

                SafeBathScreen.CALIBRATION -> ToiletCalibrationScreen(onConfirm = { x, y ->
                    with(sharedPref.edit()) {
                        putFloat("toilet_x", x)
                        putFloat("toilet_y", y)
                        apply()
                    }
                    savedX = x
                    savedY = y
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


