package com.expenseflow.app.presentation.analytics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.expenseflow.app.data.model.MonthlyAnalyticsResponse
import com.expenseflow.app.data.repository.AnalyticsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AnalyticsViewModel @Inject constructor(
    private val analyticsRepository: AnalyticsRepository
) : ViewModel() {

    private val _monthlyAnalytics = MutableStateFlow<MonthlyAnalyticsResponse?>(null)
    val monthlyAnalytics: StateFlow<MonthlyAnalyticsResponse?> = _monthlyAnalytics.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    init {
        loadAnalytics()
    }

    fun loadAnalytics(month: Int? = null, year: Int? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = analyticsRepository.getMonthlyAnalytics(month, year)
            _isLoading.value = false
            result.onSuccess {
                _monthlyAnalytics.value = it
            }.onFailure { error ->
                _errorMessage.value = error.message ?: "Failed to load analytics data"
            }
        }
    }
}
