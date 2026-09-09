package com.expenseflow.app.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.expenseflow.app.ui.theme.AccentBlue
import com.expenseflow.app.ui.theme.BrandCoral
import com.expenseflow.app.ui.theme.BrandCoralDark
import com.expenseflow.app.ui.theme.BrandEmerald
import com.expenseflow.app.ui.theme.BrandEmeraldDark
import com.expenseflow.app.ui.theme.PillCoralBg
import com.expenseflow.app.ui.theme.PillEmeraldBg
import com.expenseflow.app.ui.theme.PillNeutralBg
import com.expenseflow.app.ui.theme.PillNeutralText
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.WarningAmber

enum class BadgeStatus {
    SAFE,
    CAUTION,
    CRITICAL,
    EXCEEDED,
    INFO,
    NEUTRAL
}

/**
 * Directional status and metric badge formatted as a full pill (9999px radius) per Design.md.
 */
@Composable
fun StatusBadge(
    text: String,
    modifier: Modifier = Modifier,
    status: BadgeStatus = BadgeStatus.NEUTRAL,
    showDot: Boolean = true,
    arrow: String? = null
) {
    val isDark = MaterialTheme.colorScheme.background.luminance() < 0.5f

    val (backgroundColor, textColor, borderColor) = when (status) {
        BadgeStatus.SAFE -> if (isDark) {
            Triple(Color(0x2210B981), BrandEmerald, Color(0x4410B981))
        } else {
            Triple(PillEmeraldBg, BrandEmeraldDark, Color(0x3310B981))
        }
        BadgeStatus.CAUTION -> if (isDark) {
            Triple(Color(0x22F59E0B), WarningAmber, Color(0x44F59E0B))
        } else {
            Triple(Color(0xFFFEF3C7), Color(0xFFD97706), Color(0x33F59E0B))
        }
        BadgeStatus.CRITICAL -> if (isDark) {
            Triple(Color(0x22F43F5E), BrandCoral, Color(0x44F43F5E))
        } else {
            Triple(PillCoralBg, BrandCoralDark, Color(0x33F43F5E))
        }
        BadgeStatus.EXCEEDED -> if (isDark) {
            Triple(Color(0x33F43F5E), BrandCoral, Color(0x66F43F5E))
        } else {
            Triple(PillCoralBg, BrandCoralDark, Color(0x66F43F5E))
        }
        BadgeStatus.INFO -> if (isDark) {
            Triple(Color(0x228B5CF6), PrimaryViolet, Color(0x448B5CF6))
        } else {
            Triple(Color(0xFFEFF4FF), AccentBlue, Color(0x333B82F6))
        }
        BadgeStatus.NEUTRAL -> if (isDark) {
            Triple(Color(0x226B7280), TextMuted, Color(0x446B7280))
        } else {
            Triple(PillNeutralBg, PillNeutralText, Color(0xFFE2E8F0))
        }
    }

    Box(
        modifier = modifier
            .background(backgroundColor, shape = CircleShape)
            .border(1.dp, borderColor, shape = CircleShape)
            .padding(horizontal = 10.dp, vertical = 4.dp),
        contentAlignment = Alignment.Center
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (arrow != null) {
                Text(
                    text = arrow,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    ),
                    color = textColor,
                    maxLines = 1,
                    softWrap = false
                )
                Spacer(modifier = Modifier.width(4.dp))
            } else if (showDot) {
                Box(
                    modifier = Modifier
                        .size(6.dp)
                        .background(textColor, shape = CircleShape)
                )
                Spacer(modifier = Modifier.width(6.dp))
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelSmall,
                color = textColor,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
                softWrap = false
            )
        }
    }
}
