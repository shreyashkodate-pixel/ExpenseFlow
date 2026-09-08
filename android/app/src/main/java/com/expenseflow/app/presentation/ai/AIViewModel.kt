package com.expenseflow.app.presentation.ai

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.expenseflow.app.data.model.AIChatMessage
import com.expenseflow.app.data.model.AIRecommendationResponse
import com.expenseflow.app.data.repository.AIRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AIViewModel @Inject constructor(
    private val aiRepository: AIRepository
) : ViewModel() {

    private val _recommendations = MutableStateFlow<AIRecommendationResponse?>(null)
    val recommendations: StateFlow<AIRecommendationResponse?> = _recommendations.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    private val _chatMessages = MutableStateFlow<List<AIChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<AIChatMessage>> = _chatMessages.asStateFlow()

    private val _isChatLoading = MutableStateFlow(false)
    val isChatLoading: StateFlow<Boolean> = _isChatLoading.asStateFlow()

    private val _suggestedFollowups = MutableStateFlow<List<String>>(
        listOf(
            "How much did I spend this month?",
            "Am I on track with my budgets?",
            "What subscriptions am I paying for?",
            "What are my biggest spending categories?"
        )
    )
    val suggestedFollowups: StateFlow<List<String>> = _suggestedFollowups.asStateFlow()

    private val _referencedDataPoints = MutableStateFlow<List<String>>(emptyList())
    val referencedDataPoints: StateFlow<List<String>> = _referencedDataPoints.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _isChatVisible = MutableStateFlow(false)
    val isChatVisible: StateFlow<Boolean> = _isChatVisible.asStateFlow()

    init {
        loadRecommendations()
    }

    fun loadRecommendations(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            if (forceRefresh) {
                _isRefreshing.value = true
            } else {
                _isLoading.value = true
            }
            _errorMessage.value = null

            val result = aiRepository.getRecommendations(forceRefresh = forceRefresh)
            result.onSuccess { response ->
                _recommendations.value = response
            }.onFailure { error ->
                _errorMessage.value = error.message ?: "Failed to fetch AI insights"
            }

            _isLoading.value = false
            _isRefreshing.value = false
        }
    }

    fun openChat() {
        _isChatVisible.value = true
    }

    fun closeChat() {
        _isChatVisible.value = false
    }

    fun sendMessage(userText: String) {
        val trimmed = userText.trim()
        if (trimmed.isBlank() || _isChatLoading.value) return

        val userMessage = AIChatMessage(role = "user", content = trimmed)
        val updatedHistory = _chatMessages.value + userMessage
        _chatMessages.value = updatedHistory

        viewModelScope.launch {
            _isChatLoading.value = true
            _errorMessage.value = null

            val result = aiRepository.sendMessage(
                message = trimmed,
                history = updatedHistory.dropLast(1)
            )

            result.onSuccess { response ->
                val assistantMessage = AIChatMessage(
                    role = "assistant",
                    content = response.reply
                )
                _chatMessages.value = _chatMessages.value + assistantMessage
                if (response.suggestedFollowups.isNotEmpty()) {
                    _suggestedFollowups.value = response.suggestedFollowups
                }
                _referencedDataPoints.value = response.dataPointsReferenced
            }.onFailure { error ->
                _errorMessage.value = error.message ?: "Failed to receive AI response"
                val errorMessage = AIChatMessage(
                    role = "assistant",
                    content = "⚠️ ${error.message ?: "Unable to process request right now. Please check backend connection."}"
                )
                _chatMessages.value = _chatMessages.value + errorMessage
            }

            _isChatLoading.value = false
        }
    }

    fun clearChat() {
        _chatMessages.value = emptyList()
        _referencedDataPoints.value = emptyList()
        _suggestedFollowups.value = listOf(
            "How much did I spend this month?",
            "Am I on track with my budgets?",
            "What subscriptions am I paying for?",
            "What are my biggest spending categories?"
        )
    }

    fun clearError() {
        _errorMessage.value = null
    }
}
