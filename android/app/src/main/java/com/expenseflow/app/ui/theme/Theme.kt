package com.expenseflow.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF93C5FD),
    onPrimary = BrandNavyDark,
    primaryContainer = PrimaryContainer,
    onPrimaryContainer = Color(0xFFDAE2FD),
    secondary = AccentEmerald,
    onSecondary = TextOnPrimary,
    secondaryContainer = AccentEmeraldDark,
    onSecondaryContainer = TextPrimary,
    tertiary = AccentBlue,
    background = BackgroundDark,
    onBackground = TextPrimary,
    surface = SurfaceDark,
    onSurface = TextPrimary,
    surfaceVariant = SurfaceElevatedDark,
    onSurfaceVariant = TextSecondary,
    outline = BorderDark,
    outlineVariant = BorderSubtle,
    error = ErrorRose,
    onError = TextOnPrimary
)

private val LightColorScheme = lightColorScheme(
    primary = BrandNavy,
    onPrimary = TextOnPrimary,
    primaryContainer = SurfaceContainerHighest,
    onPrimaryContainer = BrandNavy,
    secondary = BrandEmerald,
    onSecondary = TextOnPrimary,
    secondaryContainer = PillEmeraldBg,
    onSecondaryContainer = BrandEmeraldDark,
    tertiary = BrandCoral,
    onTertiary = TextOnPrimary,
    tertiaryContainer = PillCoralBg,
    onTertiaryContainer = BrandCoralDark,
    background = CanvasLight,
    onBackground = BrandNavyDark,
    surface = SurfaceContainerLowest,
    onSurface = BrandNavyDark,
    surfaceVariant = SurfaceContainerLow,
    onSurfaceVariant = BrandSlate,
    outline = OutlineLight,
    outlineVariant = BorderLight,
    error = BrandError,
    onError = TextOnPrimary
)

@Composable
fun ExpenseFlowTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            val statusBarBg = if (darkTheme) BackgroundDark.toArgb() else CanvasLight.toArgb()
            val navBarBg = if (darkTheme) SurfaceDark.toArgb() else SurfaceContainerLowest.toArgb()
            window.statusBarColor = statusBarBg
            window.navigationBarColor = navBarBg
            val insetsController = WindowCompat.getInsetsController(window, view)
            insetsController.isAppearanceLightStatusBars = !darkTheme
            insetsController.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
