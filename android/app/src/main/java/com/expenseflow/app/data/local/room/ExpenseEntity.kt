package com.expenseflow.app.data.local.room

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "expenses")
data class ExpenseEntity(
    @PrimaryKey
    val id: Int,
    val amount: Double,
    val categoryId: Int,
    val categoryName: String,
    val description: String,
    val notes: String? = null,
    val date: String,
    val paymentMethod: String? = null,
    val createdAt: String? = null
)
