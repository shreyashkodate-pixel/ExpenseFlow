package com.expenseflow.app.presentation.expenses

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.expenseflow.app.data.local.room.CategoryEntity
import com.expenseflow.app.data.local.room.ExpenseEntity
import com.expenseflow.app.data.repository.ExpenseRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ExpenseFilterState(
    val searchQuery: String = "",
    val selectedCategoryId: Int? = null
)

@HiltViewModel
class ExpenseListViewModel @Inject constructor(
    private val expenseRepository: ExpenseRepository
) : ViewModel() {

    val categories: StateFlow<List<CategoryEntity>> = expenseRepository.localCategories
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val filterState = MutableStateFlow(ExpenseFilterState())

    val filteredExpenses: StateFlow<List<ExpenseEntity>> = combine(
        expenseRepository.localExpenses,
        filterState
    ) { expenses, filter ->
        expenses.filter { item ->
            val matchesCategory = filter.selectedCategoryId == null || item.categoryId == filter.selectedCategoryId
            val matchesSearch = filter.searchQuery.isBlank() ||
                    item.description.contains(filter.searchQuery, ignoreCase = true) ||
                    item.categoryName.contains(filter.searchQuery, ignoreCase = true) ||
                    (item.notes?.contains(filter.searchQuery, ignoreCase = true) == true)
            matchesCategory && matchesSearch
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    private val _userMessage = MutableStateFlow<String?>(null)
    val userMessage: StateFlow<String?> = _userMessage.asStateFlow()

    init {
        refresh()
    }

    fun onSearchQueryChange(query: String) {
        filterState.value = filterState.value.copy(searchQuery = query)
    }

    fun onCategoryFilterSelect(categoryId: Int?) {
        val current = filterState.value.selectedCategoryId
        filterState.value = filterState.value.copy(
            selectedCategoryId = if (current == categoryId) null else categoryId
        )
    }

    fun getSelectedCategoryId(): Int? = filterState.value.selectedCategoryId
    fun getSearchQuery(): String = filterState.value.searchQuery

    fun refresh() {
        viewModelScope.launch {
            _isRefreshing.value = true
            expenseRepository.refreshCategories()
            expenseRepository.refreshExpenses()
            _isRefreshing.value = false
        }
    }

    fun createExpense(
        amount: Double,
        categoryId: Int,
        description: String,
        notes: String?,
        date: String,
        paymentMethod: String?,
        onSuccess: () -> Unit
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = expenseRepository.createExpense(
                amount = amount,
                categoryId = categoryId,
                description = description,
                notes = notes,
                date = date,
                paymentMethod = paymentMethod
            )
            _isLoading.value = false
            result.onSuccess {
                _userMessage.value = "Expense added successfully!"
                onSuccess()
            }.onFailure { error ->
                _userMessage.value = error.message ?: "Failed to add expense"
            }
        }
    }

    fun deleteExpense(id: Int) {
        viewModelScope.launch {
            val result = expenseRepository.deleteExpense(id)
            result.onFailure { error ->
                _userMessage.value = error.message ?: "Failed to delete expense"
            }
        }
    }

    fun exportReport(format: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = expenseRepository.exportExpenses(format)
            _isLoading.value = false
            result.onSuccess { file ->
                _userMessage.value = "Report exported to: ${file.name}"
            }.onFailure { error ->
                _userMessage.value = error.message ?: "Failed to export report"
            }
        }
    }

    fun clearMessage() {
        _userMessage.value = null
    }
}
