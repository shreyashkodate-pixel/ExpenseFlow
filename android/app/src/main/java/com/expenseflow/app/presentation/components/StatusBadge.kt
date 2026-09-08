package com.expenseflow.app.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.expenseflow.app.ui.theme.AccentBlue
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.ErrorRose
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

@Composable
fun StatusBadge(
    text: String,
    modifier: Modifier = Modifier,
    status: BadgeStatus = BadgeStatus.NEUTRAL,
    showDot: Boolean = true
) {
    val (backgroundColor, textColor, borderColor) = when (status) {
        BadgeStatus.SAFE -> Triple(Color(0x2210B981), AccentEmerald, Color(0x4410B981))
        BadgeStatus.CAUTION -> Triple(Color(0x22F59E0B), WarningAmber, Color(0x44F59E0B))
        BadgeStatus.CRITICAL -> Triple(Color(0x22F43F5E), ErrorRose, Color(0x44F43F5E))
        BadgeStatus.EXCEEDED -> Triple(Color(0x33F43F5E), ErrorRose, Color(0x66F43F5E))
        BadgeStatus.INFO -> Triple(Color(0x228B5CF6), PrimaryViolet, Color(0x448B5CF6))
        BadgeStatus.NEUTRAL -> Triple(Color(0x226B7280), TextMuted, Color(0x446B7280))
    }

    Box(
        modifier = modifier
            .background(backgroundColor, shape = RoundedCornerShape(20.dp))
            .border(1.dp, borderColor, shape = RoundedCornerShape(20.dp))
            .padding(horizontal = 10.dp, vertical = 4.dp),
        contentAlignment = Alignment.Center
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (showDot) {
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
                color = textColor
            )
        }
    }
}
