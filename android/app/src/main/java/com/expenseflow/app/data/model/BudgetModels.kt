package com.expenseflow.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class BudgetCreateRequest(
    val month: Int,
    val year: Int,
    val amount: Double,
    @SerialName("category_id")
    val categoryId: Int? = null
)

@Serializable
data class BudgetResponse(
    val id: Int,
    val month: Int,
    val year: Int,
    val amount: Double,
    @SerialName("category_id")
    val categoryId: Int? = null,
    val category: CategoryDto? = null
)

@Serializable
data class BudgetStatusItem(
    @SerialName("budget_id")
    val budgetId: Int? = null,
    @SerialName("category_id")
    val categoryId: Int? = null,
    @SerialName("category_name")
    val categoryName: String,
    @SerialName("budget_amount")
    val budgetAmount: Double,
    @SerialName("spent_amount")
    val spentAmount: Double,
    @SerialName("remaining_amount")
    val remainingAmount: Double,
    @SerialName("percentage_used")
    val percentageUsed: Double,
    @SerialName("status_level")
    val statusLevel: String
)

@Serializable
data class OverallBudgetStatusResponse(
    val month: Int,
    val year: Int,
    @SerialName("overall_budget")
    val overallBudget: BudgetStatusItem? = null,
    @SerialName("category_budgets")
    val categoryBudgets: List<BudgetStatusItem> = emptyList()
)
