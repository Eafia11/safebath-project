// 로그인 화면

package com.example.safebath

import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessibilityNew
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.HealthAndSafety
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp


// ============================== [로그인 화면] ==============================
@Composable
fun LoginScreen(onLoginSuccess: (Boolean) -> Unit) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isGuardianChecked by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.fillMaxSize().padding(30.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(Icons.Default.AccessibilityNew, contentDescription = null, modifier = Modifier.size(70.dp), tint = SafeBathTheme.PrimaryBlue)
        Spacer(modifier = Modifier.height(16.dp))
        Text("SafeBath", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.ExtraBold, color = SafeBathTheme.PrimaryBlue)
        Text("실시간 욕실 안전 관리 시스템", style = MaterialTheme.typography.bodyLarge, color = SafeBathTheme.OnSecondaryText)

        Spacer(modifier = Modifier.height(40.dp))

        // 보호자 모드 토글
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
                    Text("보호자로 로그인하기", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                }
                Switch(checked = isGuardianChecked, onCheckedChange = { isGuardianChecked = it }, colors = SwitchDefaults.colors(checkedThumbColor = SafeBathTheme.PrimaryBlue, checkedTrackColor = Color(0xFFBBDEFB)))
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = email, onValueChange = { email = it }, label = { Text("이메일 주소") },
            leadingIcon = { Icon(Icons.Default.Email, contentDescription = null, tint = SafeBathTheme.OnSecondaryText) },
            modifier = Modifier.fillMaxWidth(), singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email)
        )
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedTextField(
            value = password, onValueChange = { password = it }, label = { Text("비밀번호") },
            leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = SafeBathTheme.OnSecondaryText) },
            modifier = Modifier.fillMaxWidth(), singleLine = true, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
        )

        Spacer(modifier = Modifier.height(40.dp))

        Button(
            onClick = { onLoginSuccess(isGuardianChecked) },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = SafeBathTheme.PrimaryBlue),
            shape = MaterialTheme.shapes.medium
        ) {
            Text(if (isGuardianChecked) "보호자 계정 로그인" else "기기 연동 로그인", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}