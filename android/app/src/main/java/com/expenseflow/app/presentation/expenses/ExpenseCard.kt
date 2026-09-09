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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.expenseflow.app.data.local.room.ExpenseEntity
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.ui.theme.AmountMetricStyle
import com.expenseflow.app.ui.theme.CategoryBillsBg
import com.expenseflow.app.ui.theme.CategoryBillsText
import com.expenseflow.app.ui.theme.CategoryEducationBg
import com.expenseflow.app.ui.theme.CategoryEducationText
import com.expenseflow.app.ui.theme.CategoryEntertainmentBg
import com.expenseflow.app.ui.theme.CategoryEntertainmentText
import com.expenseflow.app.ui.theme.CategoryFoodBg
import com.expenseflow.app.ui.theme.CategoryFoodText
import com.expenseflow.app.ui.theme.CategoryHealthBg
import com.expenseflow.app.ui.theme.CategoryHealthText
import com.expenseflow.app.ui.theme.CategoryOtherBg
import com.expenseflow.app.ui.theme.CategoryOtherText
import com.expenseflow.app.ui.theme.CategoryRentBg
import com.expenseflow.app.ui.theme.CategoryRentText
import com.expenseflow.app.ui.theme.CategoryShoppingBg
import com.expenseflow.app.ui.theme.CategoryShoppingText
import com.expenseflow.app.ui.theme.CategoryTransportBg
import com.expenseflow.app.ui.theme.CategoryTransportText
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

    val (categoryBg, categoryTextColor) = when (expense.categoryName.lowercase()) {
        "food", "dining", "groceries" -> CategoryFoodBg to CategoryFoodText
        "transport", "transit", "fuel" -> CategoryTransportBg to CategoryTransportText
        "shopping", "clothing" -> CategoryShoppingBg to CategoryShoppingText
        "bills", "utilities" -> CategoryBillsBg to CategoryBillsText
        "rent", "housing" -> CategoryRentBg to CategoryRentText
        "entertainment", "leisure" -> CategoryEntertainmentBg to CategoryEntertainmentText
        "health", "medical" -> CategoryHealthBg to CategoryHealthText
        "education" -> CategoryEducationBg to CategoryEducationText
        else -> CategoryOtherBg to CategoryOtherText
    }

    GlassCard(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        backgroundColor = MaterialTheme.colorScheme.surface,
        borderColor = MaterialTheme.colorScheme.outlineVariant,
        contentPadding = 14.dp
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
                // 40x40 rounded-xl category pastel icon container (Design.md)
                Box(
                    modifier = Modifier
                        .size(42.dp)
                        .background(categoryBg, shape = RoundedCornerShape(12.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = expense.categoryName.take(1).uppercase(),
                        style = MaterialTheme.typography.titleMedium,
                        color = categoryTextColor,
                        fontWeight = FontWeight.Bold
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                Column(
                    modifier = Modifier
                        .weight(1f)
                        .padding(end = 6.dp)
                ) {
                    Text(
                        text = expense.description,
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.SemiBold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        StatusBadge(
                            text = expense.categoryName,
                            status = BadgeStatus.INFO,
                            showDot = false
                        )
                        if (!expense.paymentMethod.isNullOrBlank()) {
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
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // Amount with tabular numerical figures and delete
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "- $formattedAmount",
                    style = AmountMetricStyle.copy(
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.tertiary
                    ),
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
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
