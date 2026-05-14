package com.signalnoise.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val SignalBlue = Color(0xFF4FC3F7)
val SignalBlueDim = Color(0xFF1A3A4A)
val SignalBlueBubble = Color(0xFF1E3D50)

val NoiseAmber = Color(0xFFFFB74D)
val NoiseAmberDim = Color(0xFF3A2800)
val NoiseAmberBubble = Color(0xFF3D2E00)

val Background = Color(0xFF0F0F14)
val Surface = Color(0xFF1A1A22)
val OnSurface = Color(0xFFE8E8F0)
val Subtle = Color(0xFF5A5A72)

private val DarkColors = darkColorScheme(
    primary = SignalBlue,
    background = Background,
    surface = Surface,
    onBackground = OnSurface,
    onSurface = OnSurface,
)

@Composable
fun SignalNoiseTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = DarkColors, content = content)
}
