package com.expenseflow.app.presentation.main

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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.automirrored.filled.ReceiptLong
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Savings
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.ai.AIChatBottomSheet
import com.expenseflow.app.presentation.ai.AIInsightsCard
import com.expenseflow.app.presentation.ai.AIViewModel
import com.expenseflow.app.presentation.analytics.AnalyticsScreen
import com.expenseflow.app.presentation.analytics.AnalyticsViewModel
import com.expenseflow.app.presentation.budget.BudgetScreen
import com.expenseflow.app.presentation.budget.BudgetViewModel
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.presentation.expenses.ExpenseListViewModel
import com.expenseflow.app.presentation.expenses.ExpensesScreen
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.BackgroundDark
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.SurfaceDark
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    authRepository: AuthRepository,
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
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    Scaffold(
        containerColor = BackgroundDark,
        bottomBar = {
            NavigationBar(
                containerColor = SurfaceDark,
                tonalElevation = 8.dp
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(Icons.Default.Dashboard, contentDescription = "Dashboard") },
                    label = { Text("Home") },
                    colors = navigationBarColors()
                )

                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(Icons.AutoMirrored.Filled.ReceiptLong, contentDescription = "Expenses") },
                    label = { Text("Expenses") },
                    colors = navigationBarColors()
                )

                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Icon(Icons.Default.Savings, contentDescription = "Budgets") },
                    label = { Text("Budgets") },
                    colors = navigationBarColors()
                )

                NavigationBarItem(
                    selected = selectedTab == 3,
                    onClick = { selectedTab = 3 },
                    icon = { Icon(Icons.Default.BarChart, contentDescription = "Analytics") },
                    label = { Text("Analytics") },
                    colors = navigationBarColors()
                )
            }
        },
        floatingActionButton = {
            if (selectedTab == 0) {
                ExtendedFloatingActionButton(
                    onClick = { aiViewModel.openChat() },
                    containerColor = PrimaryViolet,
                    contentColor = Color.White,
                    icon = {
                        Icon(
                            imageVector = Icons.Default.AutoAwesome,
                            contentDescription = "Ask AI"
                        )
                    },
                    text = {
                        Text(
                            text = "Ask AI",
                            fontWeight = FontWeight.Bold
                        )
                    }
                )
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
                    aiViewModel = aiViewModel,
                    onNavigateToExpenses = { selectedTab = 1 },
                    onNavigateToBudgets = { selectedTab = 2 },
                    onLogout = onLogout
                )
                1 -> ExpensesScreen(viewModel = expenseViewModel)
                2 -> BudgetScreen(viewModel = budgetViewModel)
                3 -> AnalyticsScreen(viewModel = analyticsViewModel)
            }
        }

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
private fun navigationBarColors() = NavigationBarItemDefaults.colors(
    selectedIconColor = Color.White,
    selectedTextColor = PrimaryViolet,
    indicatorColor = PrimaryViolet,
    unselectedIconColor = TextMuted,
    unselectedTextColor = TextMuted
)

@Composable
private fun DashboardTab(
    authRepository: AuthRepository,
    expenseViewModel: ExpenseListViewModel,
    budgetViewModel: BudgetViewModel,
    aiViewModel: AIViewModel,
    onNavigateToExpenses: () -> Unit,
    onNavigateToBudgets: () -> Unit,
    onLogout: () -> Unit
) {
    val user = authRepository.getCurrentUser()
    val expenses by expenseViewModel.filteredExpenses.collectAsState()
    val budgetStatus by budgetViewModel.budgetStatus.collectAsState()
    val aiRecommendations by aiViewModel.recommendations.collectAsState()
    val isAILoading by aiViewModel.isLoading.collectAsState()
    val isAIRefreshing by aiViewModel.isRefreshing.collectAsState()
    val scope = rememberCoroutineScope()

    val totalSpend = remember(expenses) { expenses.sumOf { it.amount } }
    val currencyFormatter = remember { NumberFormat.getCurrencyInstance(Locale("en", "IN")) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
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
                    text = "Welcome back,",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
                Text(
                    text = user?.fullName ?: user?.email?.substringBefore("@") ?: "User",
                    style = MaterialTheme.typography.headlineMedium,
                    color = TextPrimary,
                    fontWeight = FontWeight.Bold
                )
            }
            StatusBadge(text = "Keystore Active", status = BadgeStatus.SAFE)
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Total Spend Hero Card
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            backgroundColor = Color(0xFF151D2C)
        ) {
            Column {
                Text(
                    text = "TOTAL LOGGED SPEND",
                    style = MaterialTheme.typography.labelMedium,
                    color = TextMuted,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = currencyFormatter.format(totalSpend),
                    style = MaterialTheme.typography.displayLarge,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "${expenses.size} transactions synced with PostgreSQL",
                    style = MaterialTheme.typography.bodySmall,
                    color = AccentEmerald
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // AI Financial Intelligence Insights Card
        AIInsightsCard(
            recommendations = aiRecommendations,
            isLoading = isAILoading,
            isRefreshing = isAIRefreshing,
            onRefresh = { aiViewModel.loadRecommendations(forceRefresh = true) },
            onOpenChat = { aiViewModel.openChat() }
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Budget Pacing Quick Card
        val overall = budgetStatus?.overallBudget
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            onClick = onNavigateToBudgets
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Monthly Budget Pacing",
                        style = MaterialTheme.typography.titleMedium,
                        color = TextPrimary,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (overall != null) {
                            "${"%.1f".format(overall.percentageUsed)}% used (${currencyFormatter.format(overall.spentAmount)} / ${currencyFormatter.format(overall.budgetAmount)})"
                        } else {
                            "No budget target set. Tap to configure."
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
                Spacer(modifier = Modifier.width(8.dp))
                StatusBadge(
                    text = overall?.statusLevel?.uppercase() ?: "SETUP",
                    status = when (overall?.statusLevel) {
                        "ok" -> BadgeStatus.SAFE
                        "warning" -> BadgeStatus.CAUTION
                        "exceeded" -> BadgeStatus.CRITICAL
                        else -> BadgeStatus.INFO
                    }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Manage Transactions Card
        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            onClick = onNavigateToExpenses
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Manage Transactions",
                        style = MaterialTheme.typography.titleMedium,
                        color = TextPrimary,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Log expenses, filter categories, export PDF/CSV",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
                StatusBadge(text = "EXPENSES", status = BadgeStatus.INFO)
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Sign Out Button
        PrimaryButton(
            text = "Sign Out",
            leadingIcon = {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ExitToApp,
                    contentDescription = "Sign Out"
                )
            },
            onClick = {
                scope.launch {
                    authRepository.logout()
                    onLogout()
                }
            }
        )

        Spacer(modifier = Modifier.height(48.dp))
    }
}
