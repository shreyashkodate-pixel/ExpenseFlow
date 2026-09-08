package com.expenseflow.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CategorySpendingItem(
    @SerialName("category_id")
    val categoryId: Int,
    @SerialName("category_name")
    val categoryName: String,
    val amount: Double,
    val percentage: Double,
    @SerialName("expense_count")
    val expenseCount: Int
)

@Serializable
data class DailySpendingItem(
    val date: String,
    val amount: Double,
    @SerialName("expense_count")
    val expenseCount: Int
)

@Serializable
data class MonthlySpendingItem(
    val month: Int,
    val year: Int,
    @SerialName("month_name")
    val monthName: String,
    val amount: Double,
    @SerialName("expense_count")
    val expenseCount: Int
)

@Serializable
data class MonthlyAnalyticsResponse(
    val month: Int,
    val year: Int,
    @SerialName("total_amount")
    val totalAmount: Double,
    @SerialName("expense_count")
    val expenseCount: Int,
    @SerialName("daily_breakdown")
    val dailyBreakdown: List<DailySpendingItem> = emptyList(),
    @SerialName("by_category")
    val byCategory: List<CategorySpendingItem> = emptyList()
)

@Serializable
data class DashboardSummaryResponse(
    @SerialName("current_month_spending")
    val currentMonthSpending: Double,
    @SerialName("total_expense_count")
    val totalExpenseCount: Int,
    @SerialName("budget_status")
    val budgetStatus: BudgetStatusItem? = null,
    @SerialName("top_categories")
    val topCategories: List<CategorySpendingItem> = emptyList()
)
