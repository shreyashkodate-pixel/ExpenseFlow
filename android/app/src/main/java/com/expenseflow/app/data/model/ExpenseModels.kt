package com.expenseflow.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CategoryDto(
    val id: Int,
    val name: String,
    @SerialName("expense_count")
    val expenseCount: Int = 0
)

@Serializable
data class CategoryCreateRequest(
    val name: String
)

@Serializable
data class ExpenseDto(
    val id: Int,
    val amount: Double,
    @SerialName("category_id")
    val categoryId: Int,
    val description: String,
    val notes: String? = null,
    val date: String,
    @SerialName("payment_method")
    val paymentMethod: String? = null,
    val category: CategoryDto? = null,
    @SerialName("created_at")
    val createdAt: String? = null
)

@Serializable
data class ExpenseCreateRequest(
    val amount: Double,
    @SerialName("category_id")
    val categoryId: Int,
    val description: String,
    val notes: String? = null,
    val date: String,
    @SerialName("payment_method")
    val paymentMethod: String? = null
)

@Serializable
data class ExpenseUpdateRequest(
    val amount: Double? = null,
    @SerialName("category_id")
    val categoryId: Int? = null,
    val description: String? = null,
    val notes: String? = null,
    val date: String? = null,
    @SerialName("payment_method")
    val paymentMethod: String? = null
)

@Serializable
data class PaginatedExpensesResponse(
    val items: List<ExpenseDto>,
    val total: Int,
    val page: Int,
    @SerialName("page_size")
    val pageSize: Int,
    @SerialName("total_pages")
    val totalPages: Int
)
