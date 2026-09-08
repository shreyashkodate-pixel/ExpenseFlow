package com.expenseflow.app.presentation.budget

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.expenseflow.app.data.model.BudgetStatusItem
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.ExpenseInputField
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.BackgroundDark
import com.expenseflow.app.ui.theme.ErrorRose
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.SurfaceElevatedDark
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import com.expenseflow.app.ui.theme.WarningAmber
import java.text.NumberFormat
import java.util.Locale

@Composable
fun BudgetScreen(
    viewModel: BudgetViewModel
) {
    val budgetStatus by viewModel.budgetStatus.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val userMessage by viewModel.userMessage.collectAsState()

    val snackbarHostState = remember { SnackbarHostState() }
    var showSetBudgetDialog by remember { mutableStateOf(false) }

    LaunchedEffect(userMessage) {
        if (userMessage != null) {
            snackbarHostState.showSnackbar(userMessage!!)
            viewModel.clearMessage()
        }
    }

    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = BackgroundDark
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp)
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Budget Planner",
                        style = MaterialTheme.typography.headlineMedium,
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Monitor pacing and safe spending targets",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }

                IconButton(
                    onClick = { viewModel.loadBudgetStatus() },
                    modifier = Modifier
                        .background(SurfaceElevatedDark, CircleShape)
                        .size(38.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = "Refresh",
                        tint = PrimaryViolet,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            val overall = budgetStatus?.overallBudget

            if (overall == null) {
                // No overall budget set yet
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "No Monthly Budget Target Set",
                            style = MaterialTheme.typography.titleMedium,
                            color = TextPrimary,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "Set a monthly target to track burn rate and avoid overspending.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        Spacer(modifier = Modifier.height(18.dp))
                        PrimaryButton(
                            text = "Set Monthly Budget",
                            onClick = { showSetBudgetDialog = true }
                        )
                    }
                }
            } else {
                // Overall Budget Pacing Hero Card
                val progressFraction = (overall.percentageUsed / 100.0).coerceIn(0.0, 1.0).toFloat()
                val (statusColor, badgeStatus) = when (overall.statusLevel) {
                    "ok" -> Pair(AccentEmerald, BadgeStatus.SAFE)
                    "warning" -> Pair(WarningAmber, BadgeStatus.CAUTION)
                    else -> Pair(ErrorRose, BadgeStatus.CRITICAL)
                }

                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    backgroundColor = Color(0xFF151D2C)
                ) {
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = "OVERALL MONTHLY BUDGET",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextMuted,
                                    fontWeight = FontWeight.Bold
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = currencyFormatter.format(overall.budgetAmount),
                                    style = MaterialTheme.typography.displayMedium,
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            StatusBadge(
                                text = overall.statusLevel.uppercase(),
                                status = badgeStatus
                            )
                        }

                        Spacer(modifier = Modifier.height(18.dp))

                        // Progress Bar
                        LinearProgressIndicator(
                            progress = { progressFraction },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(10.dp),
                            color = statusColor,
                            trackColor = Color(0xFF2D3748)
                        )

                        Spacer(modifier = Modifier.height(14.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text(
                                    text = "Spent",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextMuted
                                )
                                Text(
                                    text = currencyFormatter.format(overall.spentAmount),
                                    style = MaterialTheme.typography.titleMedium,
                                    color = Color.White,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }

                            Column(horizontalAlignment = Alignment.End) {
                                Text(
                                    text = if (overall.remainingAmount >= 0) "Remaining" else "Over Budget",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = TextMuted
                                )
                                Text(
                                    text = currencyFormatter.format(overall.remainingAmount),
                                    style = MaterialTheme.typography.titleMedium,
                                    color = if (overall.remainingAmount >= 0) AccentEmerald else ErrorRose,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "${"%.1f".format(overall.percentageUsed)}% of budget utilized",
                                style = MaterialTheme.typography.bodySmall,
                                color = statusColor
                            )

                            IconButton(
                                onClick = { showSetBudgetDialog = true },
                                modifier = Modifier.size(32.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Edit,
                                    contentDescription = "Edit Budget",
                                    tint = PrimaryViolet,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Category-Specific Budgets
            val categoryBudgets = budgetStatus?.categoryBudgets.orEmpty()
            if (categoryBudgets.isNotEmpty()) {
                Text(
                    text = "Category Budget Allocations",
                    style = MaterialTheme.typography.headlineSmall,
                    color = TextPrimary,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(12.dp))

                for (catBudget in categoryBudgets) {
                    CategoryBudgetCard(item = catBudget, formatter = currencyFormatter)
                    Spacer(modifier = Modifier.height(10.dp))
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }

        // Set Budget Dialog
        if (showSetBudgetDialog) {
            SetBudgetDialog(
                currentAmount = budgetStatus?.overallBudget?.budgetAmount,
                onDismiss = { showSetBudgetDialog = false },
                onConfirm = { amount ->
                    viewModel.setBudgetTarget(amount = amount) {
                        showSetBudgetDialog = false
                    }
                },
                isLoading = isLoading
            )
        }
    }
}

@Composable
private fun CategoryBudgetCard(
    item: BudgetStatusItem,
    formatter: NumberFormat
) {
    val progressFraction = (item.percentageUsed / 100.0).coerceIn(0.0, 1.0).toFloat()
    val statusColor = when (item.statusLevel) {
        "ok" -> AccentEmerald
        "warning" -> WarningAmber
        else -> ErrorRose
    }

    GlassCard(
        modifier = Modifier.fillMaxWidth(),
        backgroundColor = SurfaceElevatedDark
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = item.categoryName,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimary,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "${"%.1f".format(item.percentageUsed)}%",
                    style = MaterialTheme.typography.labelMedium,
                    color = statusColor,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            LinearProgressIndicator(
                progress = { progressFraction },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp),
                color = statusColor,
                trackColor = Color(0xFF2D3748)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${formatter.format(item.spentAmount)} spent",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextMuted
                )
                Text(
                    text = "Limit: ${formatter.format(item.budgetAmount)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
        }
    }
}

@Composable
private fun SetBudgetDialog(
    currentAmount: Double?,
    onDismiss: () -> Unit,
    onConfirm: (Double) -> Unit,
    isLoading: Boolean
) {
    var amountText by remember { mutableStateOf(currentAmount?.toString() ?: "") }
    var errorText by remember { mutableStateOf<String?>(null) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Set Monthly Budget Target",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimary
            )
        },
        text = {
            Column {
                Text(
                    text = "Enter your total target spending limit for this month in rupees (₹).",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
                Spacer(modifier = Modifier.height(16.dp))
                ExpenseInputField(
                    value = amountText,
                    onValueChange = {
                        amountText = it
                        errorText = null
                    },
                    label = "Monthly Target (₹)",
                    placeholder = "e.g. 50000",
                    isError = errorText != null,
                    errorMessage = errorText,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Decimal,
                        imeAction = ImeAction.Done
                    )
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    val amt = amountText.toDoubleOrNull()
                    if (amt == null || amt <= 0) {
                        errorText = "Please enter a valid amount greater than ₹0"
                        return@TextButton
                    }
                    onConfirm(amt)
                },
                enabled = !isLoading
            ) {
                Text(text = "Save Target", color = PrimaryViolet, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss, enabled = !isLoading) {
                Text(text = "Cancel", color = TextMuted)
            }
        },
        containerColor = SurfaceElevatedDark
    )
}
