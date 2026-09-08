package com.expenseflow.app.presentation.budget

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.expenseflow.app.data.model.OverallBudgetStatusResponse
import com.expenseflow.app.data.repository.BudgetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Calendar
import javax.inject.Inject

@HiltViewModel
class BudgetViewModel @Inject constructor(
    private val budgetRepository: BudgetRepository
) : ViewModel() {

    private val _budgetStatus = MutableStateFlow<OverallBudgetStatusResponse?>(null)
    val budgetStatus: StateFlow<OverallBudgetStatusResponse?> = _budgetStatus.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _userMessage = MutableStateFlow<String?>(null)
    val userMessage: StateFlow<String?> = _userMessage.asStateFlow()

    init {
        loadBudgetStatus()
    }

    fun loadBudgetStatus(month: Int? = null, year: Int? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = budgetRepository.getBudgetStatus(month, year)
            _isLoading.value = false
            result.onSuccess {
                _budgetStatus.value = it
            }.onFailure { error ->
                _userMessage.value = error.message ?: "Failed to load budget status"
            }
        }
    }

    fun setBudgetTarget(
        amount: Double,
        categoryId: Int? = null,
        onSuccess: () -> Unit
    ) {
        val calendar = Calendar.getInstance()
        val currentMonth = calendar.get(Calendar.MONTH) + 1
        val currentYear = calendar.get(Calendar.YEAR)

        viewModelScope.launch {
            _isLoading.value = true
            val result = budgetRepository.createOrUpdateBudget(
                month = currentMonth,
                year = currentYear,
                amount = amount,
                categoryId = categoryId
            )
            _isLoading.value = false
            result.onSuccess {
                _userMessage.value = "Budget target updated successfully!"
                loadBudgetStatus()
                onSuccess()
            }.onFailure { error ->
                _userMessage.value = error.message ?: "Failed to set budget target"
            }
        }
    }

    fun clearMessage() {
        _userMessage.value = null
    }
}
