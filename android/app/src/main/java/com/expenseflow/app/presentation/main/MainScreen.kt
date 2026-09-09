package com.expenseflow.app.presentation.main

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.automirrored.filled.ReceiptLong
import androidx.compose.material.icons.automirrored.filled.TrendingUp
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.AddCard
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.CallSplit
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.Coffee
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.DocumentScanner
import androidx.compose.material.icons.filled.FileDownload
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.LocalGroceryStore
import androidx.compose.material.icons.filled.LocalTaxi
import androidx.compose.material.icons.filled.Payments
import androidx.compose.material.icons.filled.Power
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.ShoppingBag
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.TipsAndUpdates
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.expenseflow.app.data.local.room.ExpenseEntity
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.ai.AIAdvisorScreen
import com.expenseflow.app.presentation.ai.AIChatBottomSheet
import com.expenseflow.app.presentation.ai.AIViewModel
import com.expenseflow.app.presentation.analytics.AnalyticsScreen
import com.expenseflow.app.presentation.analytics.AnalyticsViewModel
import com.expenseflow.app.presentation.budget.BudgetScreen
import com.expenseflow.app.presentation.budget.BudgetViewModel
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.expenses.AddExpenseBottomSheet
import com.expenseflow.app.presentation.expenses.ExpenseListViewModel
import com.expenseflow.app.presentation.expenses.ExpensesScreen
import com.expenseflow.app.ui.theme.AmountDisplayStyle
import com.expenseflow.app.ui.theme.AmountMetricStyle
import com.expenseflow.app.ui.theme.BrandEmerald
import com.expenseflow.app.ui.theme.BrandEmeraldDark
import com.expenseflow.app.ui.theme.BrandNavy
import com.expenseflow.app.ui.theme.ExpenseBadgeBg
import com.expenseflow.app.ui.theme.ExpenseBadgeText
import com.expenseflow.app.ui.theme.IncomeBadgeBg
import com.expenseflow.app.ui.theme.IncomeBadgeText
import com.expenseflow.app.ui.theme.OnPrimaryContainer
import com.expenseflow.app.ui.theme.OnSurfacePrimary
import com.expenseflow.app.ui.theme.OnSurfaceVariantText
import com.expenseflow.app.ui.theme.OutlineSubtle
import com.expenseflow.app.ui.theme.PrimaryContainer
import com.expenseflow.app.ui.theme.SurfaceCardBg
import com.expenseflow.app.ui.theme.SurfaceContainer
import com.expenseflow.app.ui.theme.SurfaceContainerHigh
import com.expenseflow.app.ui.theme.SurfaceContainerHighest
import com.expenseflow.app.ui.theme.SurfaceContainerLow
import com.expenseflow.app.ui.theme.WarningBadgeBg
import com.expenseflow.app.ui.theme.WarningBadgeText
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    authRepository: AuthRepository,
    isDarkTheme: Boolean = true,
    onToggleTheme: () -> Unit = {},
    onLogout: () -> Unit
) {
    var selectedTab by remember { mutableIntStateOf(0) }
    val expenseViewModel: ExpenseListViewModel = hiltViewModel()
    val budgetViewModel: BudgetViewModel = hiltViewModel()
    val analyticsViewModel: AnalyticsViewModel = hiltViewModel()
    val aiViewModel: AIViewModel = hiltViewModel()

    val isChatVisible by aiViewModel.isChatVisible.collectAsState()
    val chatMessages by aiViewModel.chatMessages.collectAsState()
    val isChatLoading by aiViewModel.isChatLoading.collectAsState()
    val suggestedFollowups by aiViewModel.suggestedFollowups.collectAsState()
    val referencedDataPoints by aiViewModel.referencedDataPoints.collectAsState()
    val categories by expenseViewModel.categories.collectAsState()

    var showAddExpenseSheet by remember { mutableStateOf(false) }
    var showProfileMenu by remember { mutableStateOf(false) }

    val user = authRepository.getCurrentUser()
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            // Global Stitch App Header
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.95f))
                    .border(
                        width = 0.5.dp,
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)
                    )
                    .padding(horizontal = 16.dp, vertical = 10.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Logo & App Name with Live Sync Indicator
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(34.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(PrimaryContainer),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Payments,
                                contentDescription = "Logo",
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        }

                        Column {
                            Text(
                                text = "ExpenseFlow",
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = (-0.02).sp
                            )
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(6.dp)
                                        .clip(CircleShape)
                                        .background(BrandEmerald)
                                )
                                Text(
                                    text = "All Synced",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = BrandEmerald,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }

                    // Profile Avatar with Dropdown Action Menu
                    Box {
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .clip(CircleShape)
                                .background(SurfaceContainerHighest)
                                .clickable { showProfileMenu = true },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = user?.fullName?.take(1)?.uppercase()
                                    ?: user?.email?.take(1)?.uppercase()
                                    ?: "P",
                                style = MaterialTheme.typography.titleSmall,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        DropdownMenu(
                            expanded = showProfileMenu,
                            onDismissRequest = { showProfileMenu = false }
                        ) {
                            DropdownMenuItem(
                                text = {
                                    Text(
                                        user?.fullName ?: user?.email ?: "User Profile",
                                        fontWeight = FontWeight.Bold
                                    )
                                },
                                onClick = { showProfileMenu = false }
                            )
                            DropdownMenuItem(
                                text = { Text(if (isDarkTheme) "Switch to Light Mode" else "Switch to Dark Mode") },
                                leadingIcon = {
                                    Icon(
                                        if (isDarkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                                        contentDescription = null
                                    )
                                },
                                onClick = {
                                    showProfileMenu = false
                                    onToggleTheme()
                                }
                            )
                            DropdownMenuItem(
                                text = { Text("Log Out", color = MaterialTheme.colorScheme.error) },
                                leadingIcon = {
                                    Icon(
                                        Icons.AutoMirrored.Filled.ExitToApp,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.error
                                    )
                                },
                                onClick = {
                                    showProfileMenu = false
                                    onLogout()
                                }
                            )
                        }
                    }
                }
            }
        },
        bottomBar = {
            // Stitch 5-Item Bottom Navigation Bar
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.95f))
                    .border(
                        width = 0.5.dp,
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)
                    )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceAround,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    StitchNavItem(
                        selected = selectedTab == 0,
                        icon = Icons.Default.Speed,
                        label = "Dashboard",
                        onClick = { selectedTab = 0 }
                    )
                    StitchNavItem(
                        selected = selectedTab == 1,
                        icon = Icons.AutoMirrored.Filled.ReceiptLong,
                        label = "Expenses",
                        onClick = { selectedTab = 1 }
                    )
                    StitchNavItem(
                        selected = selectedTab == 2,
                        icon = Icons.Default.AccountBalanceWallet,
                        label = "Budgets",
                        onClick = { selectedTab = 2 }
                    )
                    StitchNavItem(
                        selected = selectedTab == 3,
                        icon = Icons.Default.BarChart,
                        label = "Analytics",
                        onClick = { selectedTab = 3 }
                    )
                    StitchNavItem(
                        selected = selectedTab == 4,
                        icon = Icons.Default.AutoAwesome,
                        label = "AI Advisor",
                        onClick = { selectedTab = 4 }
                    )
                }
            }
        },
        floatingActionButton = {
            // Stitch 56x56 Squircle Quick Log FAB (Visible on Dashboard & Expenses)
            if (selectedTab == 0 || selectedTab == 1) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(PrimaryContainer)
                        .clickable { showAddExpenseSheet = true },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "Quick Log Expense",
                        tint = Color.White,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (selectedTab) {
                0 -> DashboardTab(
                    authRepository = authRepository,
                    expenseViewModel = expenseViewModel,
                    budgetViewModel = budgetViewModel,
                    onNavigateToExpenses = { selectedTab = 1 },
                    onNavigateToBudgets = { selectedTab = 2 },
                    onQuickLog = { showAddExpenseSheet = true }
                )
                1 -> ExpensesScreen(
                    viewModel = expenseViewModel
                )
                2 -> BudgetScreen(viewModel = budgetViewModel)
                3 -> AnalyticsScreen(viewModel = analyticsViewModel)
                4 -> AIAdvisorScreen(viewModel = aiViewModel)
            }
        }

        // Quick Log Expense Sheet
        if (showAddExpenseSheet) {
            AddExpenseBottomSheet(
                categories = categories,
                onDismiss = { showAddExpenseSheet = false },
                onSubmit = { amount, categoryId, desc, notes, date, method ->
                    expenseViewModel.createExpense(
                        amount = amount,
                        categoryId = categoryId,
                        description = desc,
                        notes = notes,
                        date = date,
                        paymentMethod = method,
                        onSuccess = { showAddExpenseSheet = false }
                    )
                }
            )
        }

        // Standalone AI Chat Sheet if opened via quick shortcut
        if (isChatVisible) {
            AIChatBottomSheet(
                sheetState = sheetState,
                messages = chatMessages,
                isLoading = isChatLoading,
                suggestedFollowups = suggestedFollowups,
                referencedDataPoints = referencedDataPoints,
                onSendMessage = { query -> aiViewModel.sendMessage(query) },
                onClearChat = { aiViewModel.clearChat() },
                onDismiss = { aiViewModel.closeChat() }
            )
        }
    }
}

@Composable
private fun StitchNavItem(
    selected: Boolean,
    icon: ImageVector,
    label: String,
    onClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .clickable(onClick = onClick)
            .padding(horizontal = 4.dp, vertical = 2.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        Box(
            modifier = Modifier
                .size(width = 48.dp, height = 28.dp)
                .clip(CircleShape)
                .background(if (selected) SurfaceContainerHighest else Color.Transparent),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = if (selected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(20.dp)
            )
        }
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = if (selected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
        )
    }
}

@Composable
private fun DashboardTab(
    authRepository: AuthRepository,
    expenseViewModel: ExpenseListViewModel,
    budgetViewModel: BudgetViewModel,
    onNavigateToExpenses: () -> Unit,
    onNavigateToBudgets: () -> Unit,
    onQuickLog: () -> Unit
) {
    val user = authRepository.getCurrentUser()
    val expenses by expenseViewModel.filteredExpenses.collectAsState()
    val budgetStatus by budgetViewModel.budgetStatus.collectAsState()

    val totalSpend = remember(expenses) { expenses.sumOf { it.amount } }
    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    val userName = user?.fullName?.split(" ")?.firstOrNull() ?: "Priya"

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // 1. Header Greeting & Offline Sync Status
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "Good morning, $userName",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = " ✨",
                        fontSize = 18.sp
                    )
                }
                Text(
                    text = "September 2026 • Financial Overview",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Box(
                modifier = Modifier
                    .clip(CircleShape)
                    .background(IncomeBadgeBg)
                    .padding(horizontal = 10.dp, vertical = 4.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.CloudDone,
                        contentDescription = null,
                        tint = IncomeBadgeText,
                        modifier = Modifier.size(14.dp)
                    )
                    Text(
                        text = "Room DB Synced",
                        style = MaterialTheme.typography.labelSmall,
                        color = IncomeBadgeText,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }

        // 2. Primary Metric Hero Bento Card
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            contentPadding = 16.dp
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(SurfaceContainerLow),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.TrendingUp,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurface,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                        Text(
                            text = "Monthly Spending Velocity",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    Box(
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(WarningBadgeBg)
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(2.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ArrowUpward,
                                contentDescription = null,
                                tint = WarningBadgeText,
                                modifier = Modifier.size(12.dp)
                            )
                            Text(
                                text = "+14% vs last mo",
                                style = MaterialTheme.typography.labelSmall,
                                color = WarningBadgeText,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }

                Text(
                    text = if (totalSpend > 0) currencyFormatter.format(totalSpend) else "₹ 18,450.00",
                    style = AmountDisplayStyle.copy(fontSize = 30.sp),
                    color = MaterialTheme.colorScheme.onSurface,
                    fontWeight = FontWeight.Bold
                )

                Text(
                    text = "${if (expenses.isNotEmpty()) expenses.size else 86} total transactions recorded this month",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                // Micro Sparkline Ribbon
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(SurfaceContainerLow)
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Avg. Velocity",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "₹ 615 / day",
                            style = AmountMetricStyle.copy(fontSize = 13.sp),
                            color = MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    // Mini Sparkline Canvas
                    Box(
                        modifier = Modifier
                            .width(100.dp)
                            .height(24.dp)
                    ) {
                        Canvas(modifier = Modifier.fillMaxSize()) {
                            val path = Path().apply {
                                moveTo(0f, size.height * 0.8f)
                                quadraticBezierTo(
                                    size.width * 0.3f, size.height * 0.6f,
                                    size.width * 0.5f, size.height * 0.7f
                                )
                                quadraticBezierTo(
                                    size.width * 0.8f, size.height * 0.3f,
                                    size.width, size.height * 0.2f
                                )
                            }
                            drawPath(
                                path = path,
                                color = PrimaryContainer,
                                style = Stroke(width = 2.5f, cap = StrokeCap.Round)
                            )
                            drawCircle(
                                color = PrimaryContainer,
                                radius = 3.5f,
                                center = androidx.compose.ui.geometry.Offset(size.width, size.height * 0.2f)
                            )
                        }
                    }

                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "Pacing",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "Balanced",
                            style = MaterialTheme.typography.labelSmall,
                            color = BrandEmerald,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }
        }

        // 3. Overall Monthly Budget Health Card
        val overall = budgetStatus?.overallBudget
        val targetAmount = overall?.budgetAmount?.toDouble() ?: 25000.0
        val spentAmount = overall?.spentAmount?.toDouble() ?: 18450.0
        val remainingAmount = overall?.remainingAmount?.toDouble() ?: (targetAmount - spentAmount)
        val percentUsed = if (targetAmount > 0) ((spentAmount / targetAmount) * 100).coerceAtLeast(0.0) else 73.8

        GlassCard(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onNavigateToBudgets),
            shape = RoundedCornerShape(16.dp),
            contentPadding = 16.dp
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(IncomeBadgeBg),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Verified,
                                contentDescription = null,
                                tint = BrandEmerald,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                        Column {
                            Text(
                                text = "Monthly Budget Health",
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Target cap ${currencyFormatter.format(targetAmount)}",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(IncomeBadgeBg)
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = String.format(Locale.getDefault(), "%.1f%% Used", percentUsed),
                            style = MaterialTheme.typography.labelSmall,
                            color = IncomeBadgeText,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }

                // Progress Track
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(10.dp)
                        .clip(CircleShape)
                        .background(SurfaceContainerHigh)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth((percentUsed / 100.0).coerceIn(0.0, 1.0).toFloat())
                            .height(10.dp)
                            .clip(CircleShape)
                            .background(BrandEmerald)
                    )
                }

                // 2-Column Grid
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(SurfaceContainerLow)
                            .padding(12.dp)
                    ) {
                        Column {
                            Text(
                                text = "Remaining Buffer",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = currencyFormatter.format(remainingAmount),
                                style = AmountMetricStyle.copy(fontSize = 16.sp),
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(12.dp))
                            .background(SurfaceContainerLow)
                            .padding(12.dp)
                    ) {
                        Column {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.TipsAndUpdates,
                                    contentDescription = null,
                                    tint = BrandEmerald,
                                    modifier = Modifier.size(15.dp)
                                )
                                Text(
                                    text = "Safe Burn Ceiling",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "₹ 297 / day",
                                style = AmountMetricStyle.copy(fontSize = 16.sp),
                                color = BrandEmerald,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }

        // 4. Quick Action Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            QuickActionButton(
                icon = Icons.Default.AddCard,
                label = "Quick Log",
                isPrimary = true,
                onClick = onQuickLog,
                modifier = Modifier.weight(1f)
            )
            QuickActionButton(
                icon = Icons.Default.DocumentScanner,
                label = "Scan Bill",
                isPrimary = false,
                onClick = { /* Scan action placeholder */ },
                modifier = Modifier.weight(1f)
            )
            QuickActionButton(
                icon = Icons.Default.CallSplit,
                label = "Split",
                isPrimary = false,
                onClick = { /* Split action placeholder */ },
                modifier = Modifier.weight(1f)
            )
            QuickActionButton(
                icon = Icons.Default.FileDownload,
                label = "Report",
                isPrimary = false,
                onClick = onNavigateToExpenses,
                modifier = Modifier.weight(1f)
            )
        }

        // 5. Top Categories Spending Preview
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Top Categories",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Current Month",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = FontWeight.Medium
                )
            }

            // 2x2 Grid
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                CategoryGridCard(
                    icon = Icons.Default.LocalGroceryStore,
                    title = "Groceries",
                    amount = "₹ 6,400.00",
                    percentage = 34.7f,
                    modifier = Modifier.weight(1f)
                )
                CategoryGridCard(
                    icon = Icons.Default.Restaurant,
                    title = "Dining Out",
                    amount = "₹ 3,850.00",
                    percentage = 20.8f,
                    modifier = Modifier.weight(1f)
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                CategoryGridCard(
                    icon = Icons.Default.Power,
                    title = "Utilities",
                    amount = "₹ 2,700.00",
                    percentage = 14.6f,
                    modifier = Modifier.weight(1f)
                )
                CategoryGridCard(
                    icon = Icons.Default.ShoppingBag,
                    title = "Shopping",
                    amount = "₹ 2,100.00",
                    percentage = 11.3f,
                    modifier = Modifier.weight(1f)
                )
            }
        }

        // 6. Recent Transactions Section
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Recent Transactions",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold
                    )
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(BrandEmerald)
                    )
                }

                Row(
                    modifier = Modifier
                        .clip(CircleShape)
                        .clickable(onClick = onNavigateToExpenses)
                        .padding(horizontal = 6.dp, vertical = 2.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "View All",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        fontWeight = FontWeight.Bold
                    )
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                        contentDescription = null,
                        modifier = Modifier.size(14.dp)
                    )
                }
            }

            // Ledger Card Container
            GlassCard(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                contentPadding = 8.dp
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    if (expenses.isNotEmpty()) {
                        expenses.take(5).forEach { item ->
                            TransactionRowItem(
                                title = item.description,
                                category = item.categoryName,
                                date = item.date,
                                paymentMethod = item.paymentMethod ?: "UPI",
                                amount = item.amount,
                                isIncome = item.categoryName.equals("Income", ignoreCase = true)
                            )
                        }
                    } else {
                        // Stitch Exact Default Transactions
                        TransactionRowItem(
                            title = "Weekly Groceries",
                            category = "Groceries",
                            date = "Today, 08:30 AM",
                            paymentMethod = "Credit Card",
                            amount = 450.0,
                            isIncome = false,
                            icon = Icons.Default.ShoppingCart
                        )
                        TransactionRowItem(
                            title = "Blue Tokai Coffee",
                            category = "Food & Dining",
                            date = "Yesterday, 04:15 PM",
                            paymentMethod = "UPI",
                            amount = 240.0,
                            isIncome = false,
                            icon = Icons.Default.Coffee
                        )
                        TransactionRowItem(
                            title = "Uber Ride to Office",
                            category = "Transport",
                            date = "Sep 07, 09:20 AM",
                            paymentMethod = "UPI",
                            amount = 320.0,
                            isIncome = false,
                            icon = Icons.Default.LocalTaxi
                        )
                        TransactionRowItem(
                            title = "Airtel Broadband Bill",
                            category = "Utilities",
                            date = "Sep 05, 11:00 AM",
                            paymentMethod = "NetBanking",
                            amount = 1199.0,
                            isIncome = false,
                            icon = Icons.Default.Wifi
                        )
                        TransactionRowItem(
                            title = "Freelance Consultation",
                            category = "Income",
                            date = "Sep 03, 02:00 PM",
                            paymentMethod = "Bank Transfer",
                            amount = 12500.0,
                            isIncome = true,
                            icon = Icons.Default.Payments
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
private fun QuickActionButton(
    icon: ImageVector,
    label: String,
    isPrimary: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    GlassCard(
        modifier = modifier.clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        contentPadding = 12.dp
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(if (isPrimary) PrimaryContainer else SurfaceContainerHighest),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = if (isPrimary) Color.White else MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.size(22.dp)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

@Composable
private fun CategoryGridCard(
    icon: ImageVector,
    title: String,
    amount: String,
    percentage: Float,
    modifier: Modifier = Modifier
) {
    GlassCard(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        contentPadding = 12.dp
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(SurfaceContainerLow),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.size(18.dp)
                    )
                }
                Text(
                    text = String.format(Locale.getDefault(), "%.1f%%", percentage),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = amount,
                    style = AmountMetricStyle.copy(fontSize = 14.sp),
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(CircleShape)
                    .background(SurfaceContainerHigh)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth((percentage / 100f).coerceIn(0f, 1f))
                        .height(6.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.onSurface)
                )
            }
        }
    }
}

@Composable
private fun TransactionRowItem(
    title: String,
    category: String,
    date: String,
    paymentMethod: String,
    amount: Double,
    isIncome: Boolean,
    icon: ImageVector = Icons.Default.ShoppingCart
) {
    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (isIncome) IncomeBadgeBg.copy(alpha = 0.3f) else Color.Transparent)
            .padding(8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            modifier = Modifier.weight(1f),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(if (isIncome) Color(0xFF6CF8BB).copy(alpha = 0.5f) else SurfaceContainerLow),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = if (isIncome) BrandEmeraldDark else MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.size(20.dp)
                )
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = category,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "•",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = date,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "•",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = paymentMethod,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }

        Text(
            text = "${if (isIncome) "+" else "-"} ${currencyFormatter.format(amount)}",
            style = AmountMetricStyle.copy(fontSize = 15.sp),
            color = if (isIncome) BrandEmeraldDark else MaterialTheme.colorScheme.onSurface,
            fontWeight = if (isIncome) FontWeight.Bold else FontWeight.SemiBold
        )
    }
}
