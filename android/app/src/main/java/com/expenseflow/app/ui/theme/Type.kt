package com.expenseflow.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.googlefonts.Font
import androidx.compose.ui.text.googlefonts.GoogleFont
import androidx.compose.ui.unit.sp
import com.expenseflow.app.R

// Google Font Provider with automatic fallback
private val GoogleFontProvider = GoogleFont.Provider(
    providerAuthority = "com.google.android.gms.fonts",
    providerPackage = "com.google.android.gms",
    certificates = R.array.com_google_android_gms_fonts_certs
)

val PlusJakartaSansFont = GoogleFont("Plus Jakarta Sans")
val InterFont = GoogleFont("Inter")

val PlusJakartaSansFamily = FontFamily(
    Font(googleFont = PlusJakartaSansFont, fontProvider = GoogleFontProvider, weight = FontWeight.Bold),
    Font(googleFont = PlusJakartaSansFont, fontProvider = GoogleFontProvider, weight = FontWeight.SemiBold),
    Font(googleFont = PlusJakartaSansFont, fontProvider = GoogleFontProvider, weight = FontWeight.Medium),
    Font(googleFont = PlusJakartaSansFont, fontProvider = GoogleFontProvider, weight = FontWeight.Normal)
)

val InterFamily = FontFamily(
    Font(googleFont = InterFont, fontProvider = GoogleFontProvider, weight = FontWeight.Bold),
    Font(googleFont = InterFont, fontProvider = GoogleFontProvider, weight = FontWeight.SemiBold),
    Font(googleFont = InterFont, fontProvider = GoogleFontProvider, weight = FontWeight.Medium),
    Font(googleFont = InterFont, fontProvider = GoogleFontProvider, weight = FontWeight.Normal)
)

// Design.md Tabular Numeric Feature Setting for Financial Values
const val TabularFigures = "tnum"

// Design.md Dedicated Financial Amount Styles
val AmountDisplayStyle = TextStyle(
    fontFamily = PlusJakartaSansFamily,
    fontWeight = FontWeight.Bold,
    fontSize = 36.sp,
    lineHeight = 40.sp,
    letterSpacing = (-0.03).sp,
    fontFeatureSettings = TabularFigures
)

val AmountMetricStyle = TextStyle(
    fontFamily = InterFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 20.sp,
    lineHeight = 26.sp,
    letterSpacing = (-0.02).sp,
    fontFeatureSettings = TabularFigures
)

// Material 3 Typography Hierarchy Mapped to Design.md
val Typography = Typography(
    // headline-xl (40px, 700, -0.03em)
    displayLarge = TextStyle(
        fontFamily = PlusJakartaSansFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 40.sp,
        lineHeight = 48.sp,
        letterSpacing = (-0.03).sp
    ),
    // headline-xl-mobile (32px, 700, -0.025em)
    displayMedium = TextStyle(
        fontFamily = PlusJakartaSansFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 38.sp,
        letterSpacing = (-0.025).sp
    ),
    // headline-lg (28px, 600, -0.02em)
    headlineLarge = TextStyle(
        fontFamily = PlusJakartaSansFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 34.sp,
        letterSpacing = (-0.02).sp
    ),
    // headline-lg-mobile (24px, 600, -0.02em)
    headlineMedium = TextStyle(
        fontFamily = PlusJakartaSansFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 30.sp,
        letterSpacing = (-0.02).sp
    ),
    // headline-sm (18px, 600, -0.01em)
    headlineSmall = TextStyle(
        fontFamily = PlusJakartaSansFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp,
        letterSpacing = (-0.01).sp
    ),
    // amount-metric / titleLarge (20px, 600, -0.02em)
    titleLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 26.sp,
        letterSpacing = (-0.02).sp,
        fontFeatureSettings = TabularFigures
    ),
    titleMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 22.sp
    ),
    titleSmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    // body-lg (16px, 400, -0.01em)
    bodyLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = (-0.01).sp
    ),
    // body-md (14px, 400, 0em)
    bodyMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.sp
    ),
    bodySmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),
    // body-md-medium (14px, 500, -0.005em)
    labelLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = (-0.005).sp
    ),
    // label-md (12px, 600, 0.02em)
    labelMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.02.sp
    ),
    // label-sm (11px, 600, 0.03em)
    labelSmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 11.sp,
        lineHeight = 14.sp,
        letterSpacing = 0.03.sp
    )
)
