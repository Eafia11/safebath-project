// 좌표 설정 화면

package com.example.safebath

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp


// ============================== [ 좌표 설정 화면] ==============================
@Composable
fun ToiletCalibrationScreen(onConfirm: (Float, Float) -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Top) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Text("설정", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
            Icon(Icons.Default.Settings, contentDescription = null, tint = Color.LightGray)
        }
        Spacer(modifier = Modifier.height(48.dp))
        Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = SafeBathTheme.CardBackground)) {
            Column(modifier = Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(Icons.Default.AccessibilityNew, contentDescription = null, modifier = Modifier.size(60.dp), tint = SafeBathTheme.PrimaryBlue)
                Spacer(modifier = Modifier.height(16.dp))
                Text("변기 위치 설정", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = SafeBathTheme.OnSurfaceText)
                Spacer(modifier = Modifier.height(16.dp))
                Text("변기에 앉아 아래 버튼을 눌러주세요.\nmmWave 레이더가 현재 좌표를 저장합니다.", style = MaterialTheme.typography.bodyMedium, color = SafeBathTheme.OnSecondaryText, textAlign = TextAlign.Center)
            }
        }
        Spacer(modifier = Modifier.weight(1f))
        Button(
            onClick = { onConfirm(1.25f, 0.78f) },
            modifier = Modifier.fillMaxWidth().height(60.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
            shape = MaterialTheme.shapes.medium
        ) {
            Icon(Icons.Default.LocationOn, contentDescription = null)
            Spacer(modifier = Modifier.width(12.dp))
            Text("지금 위치를 변기로 확정", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}
