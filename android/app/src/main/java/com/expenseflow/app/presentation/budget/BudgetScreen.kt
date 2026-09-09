package com.expenseflow.app.presentation.budget

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FitnessCenter
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.FormatAlignLeft
import androidx.compose.material.icons.filled.LocalGasStation
import androidx.compose.material.icons.filled.LocalGroceryStore
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.ShoppingBag
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.expenseflow.app.data.model.BudgetStatusItem
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.ui.theme.AmountDisplayStyle
import com.expenseflow.app.ui.theme.AmountMetricStyle
import com.expenseflow.app.ui.theme.BrandCoral
import com.expenseflow.app.ui.theme.BrandCoralDark
import com.expenseflow.app.ui.theme.BrandEmerald
import com.expenseflow.app.ui.theme.BrandEmeraldDark
import com.expenseflow.app.ui.theme.ExpenseBadgeBg
import com.expenseflow.app.ui.theme.ExpenseBadgeText
import com.expenseflow.app.ui.theme.IncomeBadgeBg
import com.expenseflow.app.ui.theme.IncomeBadgeText
import com.expenseflow.app.ui.theme.OutlineSubtle
import com.expenseflow.app.ui.theme.PrimaryContainer
import com.expenseflow.app.ui.theme.StatusWarning
import com.expenseflow.app.ui.theme.SurfaceContainer
import com.expenseflow.app.ui.theme.SurfaceContainerHigh
import com.expenseflow.app.ui.theme.SurfaceContainerHighest
import com.expenseflow.app.ui.theme.SurfaceContainerLow
import com.expenseflow.app.ui.theme.WarningBadgeBg
import com.expenseflow.app.ui.theme.WarningBadgeText
import java.text.NumberFormat
import java.util.Calendar
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BudgetScreen(
    viewModel: BudgetViewModel
) {
    val budgetStatus by viewModel.budgetStatus.collectAsState()
    val userMessage by viewModel.userMessage.collectAsState()

    val snackbarHostState = remember { SnackbarHostState() }
    val modalSheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var showSetTargetSheet by remember { mutableStateOf(false) }

    var selectedMonth by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.MONTH) + 1) }
    var selectedYear by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.YEAR)) }

    var targetAmountInput by remember { mutableStateOf("") }
    var selectedCategoryId by remember { mutableStateOf<Int?>(null) }
    var editingCategoryName by remember { mutableStateOf("Overall Monthly Budget") }

    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    LaunchedEffect(userMessage) {
        if (userMessage != null) {
            snackbarHostState.showSnackbar(userMessage!!)
            viewModel.clearMessage()
        }
    }

    val overall = budgetStatus?.overallBudget
    val targetBudgetAmount = overall?.budgetAmount?.toDouble() ?: 25000.0
    val spentAmount = overall?.spentAmount?.toDouble() ?: 18450.0
    val remainingAmount = overall?.remainingAmount?.toDouble() ?: (targetBudgetAmount - spentAmount)
    val percentageUsed = if (targetBudgetAmount > 0) ((spentAmount / targetBudgetAmount) * 100).coerceAtLeast(0.0) else 73.8

    val categoryBudgets = budgetStatus?.categoryBudgets ?: emptyList()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 1. Header with Month Selector & Target Trigger
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(
                        text = "Budgets & Pacing",
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = (-0.02).sp
                    )
                    Text(
                        text = "Real-time burn calibration",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(PrimaryContainer)
                        .clickable {
                            editingCategoryName = "Overall Monthly Budget"
                            selectedCategoryId = null
                            targetAmountInput = targetBudgetAmount.toInt().toString()
                            showSetTargetSheet = true
                        }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Set Target",
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = "Set Target",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color.White,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            // Month Picker Carousel
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color.White)
                    .border(1.dp, OutlineSubtle.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
                    .padding(horizontal = 12.dp, vertical = 8.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(
                        onClick = {
                            if (selectedMonth > 1) selectedMonth-- else { selectedMonth = 12; selectedYear-- }
                            viewModel.loadBudgetStatus(selectedMonth, selectedYear)
                        },
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.ChevronLeft,
                            contentDescription = "Previous Month",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CalendarMonth,
                            contentDescription = null,
                            tint = BrandEmerald,
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = "September $selectedYear",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.Bold
                        )
                        Box(
                            modifier = Modifier
                                .clip(CircleShape)
                                .background(SurfaceContainer)
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = "Day 9 of 30",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    IconButton(
                        onClick = {
                            if (selectedMonth < 12) selectedMonth++ else { selectedMonth = 1; selectedYear++ }
                            viewModel.loadBudgetStatus(selectedMonth, selectedYear)
                        },
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = "Next Month",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // 2. Master Monthly Budget Card
            GlassCard(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                contentPadding = 16.dp
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Top
                    ) {
                        Column {
                            Text(
                                text = "Overall Monthly Budget",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = currencyFormatter.format(targetBudgetAmount),
                                style = AmountDisplayStyle.copy(fontSize = 30.sp),
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "Remaining",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = currencyFormatter.format(remainingAmount),
                                style = AmountMetricStyle.copy(fontSize = 18.sp),
                                color = BrandEmerald,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }

                    // Pacing Meter Visual
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "${currencyFormatter.format(spentAmount)} spent",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Medium
                            )
                            Text(
                                text = String.format(Locale.getDefault(), "%.1f%% used", percentageUsed),
                                style = MaterialTheme.typography.labelSmall,
                                color = BrandEmerald,
                                fontWeight = FontWeight.SemiBold
                            )
                        }

                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(12.dp)
                                .clip(CircleShape)
                                .background(SurfaceContainerHigh)
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth((percentageUsed / 100.0).coerceIn(0.0, 1.0).toFloat())
                                    .height(12.dp)
                                    .clip(CircleShape)
                                    .background(BrandEmerald)
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Target: 30% pacing ideal",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = "21 days left",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    // Daily Safe Ceiling Highlight Box
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(SurfaceContainerLow)
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .background(IncomeBadgeBg),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.FormatAlignLeft,
                                contentDescription = null,
                                tint = IncomeBadgeText,
                                modifier = Modifier.size(20.dp)
                            )
                        }

                        Column {
                            Text(
                                text = "Daily Safe Ceiling",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Row(verticalAlignment = Alignment.Bottom) {
                                Text(
                                    text = "₹ 297.70",
                                    style = AmountMetricStyle.copy(fontSize = 18.sp),
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = " / day to survive month",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    modifier = Modifier.padding(start = 4.dp)
                                )
                            }
                        }
                    }
                }
            }

            // 3. Proactive AI Warning Banner
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(WarningBadgeBg)
                    .border(1.dp, StatusWarning.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
                    .padding(16.dp)
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .background(WarningBadgeText.copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Bolt,
                                contentDescription = null,
                                tint = WarningBadgeText,
                                modifier = Modifier.size(20.dp)
                            )
                        }

                        Column {
                            Text(
                                text = "Dining Out Exhaustion Warning",
                                style = MaterialTheme.typography.titleSmall,
                                color = WarningBadgeText,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "At current burn rate (₹ 577/day), your dining budget will exhaust in 5 days (Sep 14). Safe daily ceiling: ₹ 38.00/day.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(CircleShape)
                                .background(Color.White)
                                .padding(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "Snooze Alert",
                                style = MaterialTheme.typography.labelSmall,
                                color = WarningBadgeText,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Box(
                            modifier = Modifier
                                .clip(CircleShape)
                                .background(WarningBadgeText)
                                .clickable {
                                    editingCategoryName = "Dining Out"
                                    selectedCategoryId = 3
                                    targetAmountInput = "6000"
                                    showSetTargetSheet = true
                                }
                                .padding(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "Adjust Cap",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // 4. Category Allocations Section Title & Tap-to-Edit Hint
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Category Allocations",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold
                    )
                    Box(
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(SurfaceContainer)
                            .padding(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = "${categoryBudgets.size.coerceAtLeast(5)} Active",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.TouchApp,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(14.dp)
                    )
                    Text(
                        text = "Tap to recalibrate",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 5. Category Budgets List
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                if (categoryBudgets.isNotEmpty()) {
                    categoryBudgets.forEach { budgetItem ->
                        CategoryBudgetCard(
                            item = budgetItem,
                            onClick = {
                                editingCategoryName = budgetItem.categoryName
                                selectedCategoryId = budgetItem.categoryId
                                targetAmountInput = budgetItem.budgetAmount.toInt().toString()
                                showSetTargetSheet = true
                            }
                        )
                    }
                } else {
                    // Stitch Exact Mock Allocations List
                    MockCategoryBudgetCard(
                        categoryName = "Groceries",
                        cap = 6000.0,
                        spent = 5800.0,
                        percentage = 96.6f,
                        statusLevel = "warning",
                        statusText = "Warning",
                        remainingText = "₹ 200.00 left",
                        icon = Icons.Default.LocalGroceryStore,
                        onClick = {
                            editingCategoryName = "Groceries"
                            targetAmountInput = "6000"
                            showSetTargetSheet = true
                        }
                    )
                    MockCategoryBudgetCard(
                        categoryName = "Dining Out",
                        cap = 6000.0,
                        spent = 5200.0,
                        percentage = 86.7f,
                        statusLevel = "critical",
                        statusText = "Critical",
                        remainingText = "Exhausts in 5 days",
                        icon = Icons.Default.Restaurant,
                        onClick = {
                            editingCategoryName = "Dining Out"
                            targetAmountInput = "6000"
                            showSetTargetSheet = true
                        }
                    )
                    MockCategoryBudgetCard(
                        categoryName = "Utilities & Bills",
                        cap = 4500.0,
                        spent = 2700.0,
                        percentage = 60.0f,
                        statusLevel = "safe",
                        statusText = "Safe",
                        remainingText = "₹ 1,800.00 left",
                        icon = Icons.Default.FlashOn,
                        onClick = {
                            editingCategoryName = "Utilities & Bills"
                            targetAmountInput = "4500"
                            showSetTargetSheet = true
                        }
                    )
                    MockCategoryBudgetCard(
                        categoryName = "Transport & Fuel",
                        cap = 3500.0,
                        spent = 2100.0,
                        percentage = 60.0f,
                        statusLevel = "safe",
                        statusText = "Safe",
                        remainingText = "₹ 1,400.00 left",
                        icon = Icons.Default.LocalGasStation,
                        onClick = {
                            editingCategoryName = "Transport & Fuel"
                            targetAmountInput = "3500"
                            showSetTargetSheet = true
                        }
                    )
                    MockCategoryBudgetCard(
                        categoryName = "Shopping & Leisure",
                        cap = 4000.0,
                        spent = 4200.0,
                        percentage = 105.0f,
                        statusLevel = "exceeded",
                        statusText = "Exceeded",
                        remainingText = "₹ 200.00 over budget",
                        icon = Icons.Default.ShoppingBag,
                        onClick = {
                            editingCategoryName = "Shopping & Leisure"
                            targetAmountInput = "4000"
                            showSetTargetSheet = true
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))
        }

        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter)
        )

        // 6. Set / Recalibrate Budget Target Bottom Sheet Modal
        if (showSetTargetSheet) {
            ModalBottomSheet(
                onDismissRequest = { showSetTargetSheet = false },
                sheetState = modalSheetState,
                containerColor = MaterialTheme.colorScheme.surface
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Set Budget Target",
                                style = MaterialTheme.typography.titleLarge,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Target for $editingCategoryName",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        IconButton(onClick = { showSetTargetSheet = false }) {
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = "Close",
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    // Amount Input
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = "Target Budget Amount (₹)",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(SurfaceContainerLow)
                                .padding(horizontal = 14.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "₹ ",
                                style = AmountDisplayStyle.copy(fontSize = 20.sp),
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold
                            )
                            BasicTextField(
                                value = targetAmountInput,
                                onValueChange = { targetAmountInput = it.filter { ch -> ch.isDigit() || ch == '.' } },
                                modifier = Modifier.fillMaxWidth(),
                                textStyle = TextStyle(
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.Bold
                                ),
                                cursorBrush = SolidColor(PrimaryContainer)
                            )
                        }
                    }

                    // Save CTA Button
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(PrimaryContainer)
                            .clickable {
                                val amount = targetAmountInput.toDoubleOrNull()
                                if (amount != null && amount > 0) {
                                    viewModel.setBudgetTarget(
                                        amount = amount,
                                        categoryId = selectedCategoryId
                                    ) {
                                        showSetTargetSheet = false
                                    }
                                }
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Save Budget Target",
                            style = MaterialTheme.typography.titleSmall,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
private fun CategoryBudgetCard(
    item: BudgetStatusItem,
    onClick: () -> Unit
) {
    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        contentPadding = 16.dp
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(SurfaceContainerLow),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = getBudgetCategoryIcon(item.categoryName),
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurface,
                            modifier = Modifier.size(24.dp)
                        )
                    }

                    Column {
                        Text(
                            text = item.categoryName,
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Cap: ${currencyFormatter.format(item.budgetAmount)}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Column(horizontalAlignment = Alignment.End) {
                    val (badgeBg, badgeText, statusLabel) = when (item.statusLevel) {
                        "warning" -> Triple(WarningBadgeBg, WarningBadgeText, "Warning")
                        "exceeded" -> Triple(ExpenseBadgeBg, ExpenseBadgeText, "Exceeded")
                        else -> Triple(IncomeBadgeBg, IncomeBadgeText, "Safe")
                    }

                    Box(
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(badgeBg)
                            .padding(horizontal = 8.dp, vertical = 3.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(5.dp)
                                    .clip(CircleShape)
                                    .background(badgeText)
                            )
                            Text(
                                text = statusLabel,
                                style = MaterialTheme.typography.labelSmall,
                                color = badgeText,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "${currencyFormatter.format(item.remainingAmount)} left",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // Progress Bar
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                val progressColor = when (item.statusLevel) {
                    "warning" -> StatusWarning
                    "exceeded" -> BrandCoralDark
                    else -> BrandEmerald
                }

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp)
                        .clip(CircleShape)
                        .background(SurfaceContainerHigh)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth((item.percentageUsed / 100.0).coerceIn(0.0, 1.0).toFloat())
                            .height(8.dp)
                            .clip(CircleShape)
                            .background(progressColor)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "${currencyFormatter.format(item.spentAmount)} spent",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = String.format(Locale.getDefault(), "%.1f%%", item.percentageUsed),
                        style = MaterialTheme.typography.labelSmall,
                        color = progressColor,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

@Composable
private fun MockCategoryBudgetCard(
    categoryName: String,
    cap: Double,
    spent: Double,
    percentage: Float,
    statusLevel: String,
    statusText: String,
    remainingText: String,
    icon: ImageVector,
    onClick: () -> Unit
) {
    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        contentPadding = 16.dp
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(SurfaceContainerLow),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = icon,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurface,
                            modifier = Modifier.size(24.dp)
                        )
                    }

                    Column {
                        Text(
                            text = categoryName,
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Cap: ${currencyFormatter.format(cap)}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Column(horizontalAlignment = Alignment.End) {
                    val (badgeBg, badgeText) = when (statusLevel) {
                        "warning" -> Pair(WarningBadgeBg, WarningBadgeText)
                        "critical", "exceeded" -> Pair(ExpenseBadgeBg, ExpenseBadgeText)
                        else -> Pair(IncomeBadgeBg, IncomeBadgeText)
                    }

                    Box(
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(badgeBg)
                            .padding(horizontal = 8.dp, vertical = 3.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(5.dp)
                                    .clip(CircleShape)
                                    .background(badgeText)
                            )
                            Text(
                                text = statusText,
                                style = MaterialTheme.typography.labelSmall,
                                color = badgeText,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = remainingText,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // Progress Bar
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                val progressColor = when (statusLevel) {
                    "warning" -> StatusWarning
                    "critical", "exceeded" -> BrandCoralDark
                    else -> BrandEmerald
                }

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp)
                        .clip(CircleShape)
                        .background(SurfaceContainerHigh)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth((percentage / 100f).coerceIn(0f, 1f))
                            .height(8.dp)
                            .clip(CircleShape)
                            .background(progressColor)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "${currencyFormatter.format(spent)} spent",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = String.format(Locale.getDefault(), "%.1f%%", percentage),
                        style = MaterialTheme.typography.labelSmall,
                        color = progressColor,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

private fun getBudgetCategoryIcon(name: String): ImageVector {
    return when (name.lowercase()) {
        "groceries" -> Icons.Default.LocalGroceryStore
        "dining out", "food" -> Icons.Default.Restaurant
        "utilities & bills", "utilities" -> Icons.Default.FlashOn
        "transport & fuel", "transport" -> Icons.Default.LocalGasStation
        "shopping & leisure", "shopping" -> Icons.Default.ShoppingBag
        "health" -> Icons.Default.FitnessCenter
        else -> Icons.Default.LocalGroceryStore
    }
}
