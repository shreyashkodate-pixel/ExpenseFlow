package com.expenseflow.app.presentation.expenses

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Payment
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.expenseflow.app.data.local.room.ExpenseEntity
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.ui.theme.BorderSubtle
import com.expenseflow.app.ui.theme.ErrorRose
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.SurfaceElevatedDark
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ExpenseCard(
    expense: ExpenseEntity,
    onDelete: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    val indianCurrencyFormat = NumberFormat.getCurrencyInstance(Locale("en", "IN"))
    val formattedAmount = try {
        indianCurrencyFormat.format(expense.amount)
    } catch (_: Exception) {
        "₹ ${"%.2f".format(expense.amount)}"
    }

    GlassCard(
        modifier = modifier.fillMaxWidth(),
        backgroundColor = SurfaceElevatedDark,
        borderColor = BorderSubtle
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                // Category Avatar Pill
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .background(Color(0x228B5CF6), shape = CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = expense.categoryName.take(1).uppercase(),
                        style = MaterialTheme.typography.titleMedium,
                        color = PrimaryViolet,
                        fontWeight = FontWeight.Bold
                    )
                }

                Spacer(modifier = Modifier.width(14.dp))

                Column {
                    Text(
                        text = expense.description,
                        style = MaterialTheme.typography.titleMedium,
                        color = TextPrimary,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        StatusBadge(
                            text = expense.categoryName,
                            status = BadgeStatus.INFO,
                            showDot = false
                        )
                        if (!expense.paymentMethod.isNullOrBlank()) {
                            Spacer(modifier = Modifier.width(6.dp))
                            StatusBadge(
                                text = expense.paymentMethod,
                                status = BadgeStatus.NEUTRAL,
                                showDot = false
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = expense.date,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted
                    )
                }
            }

            // Amount and Delete
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "- $formattedAmount",
                    style = MaterialTheme.typography.titleMedium,
                    color = ErrorRose,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.width(4.dp))
                IconButton(
                    onClick = { onDelete(expense.id) },
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Delete expense",
                        tint = TextMuted,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
