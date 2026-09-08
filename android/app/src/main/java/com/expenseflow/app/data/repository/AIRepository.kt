package com.expenseflow.app.data.repository

import com.expenseflow.app.data.model.AIChatMessage
import com.expenseflow.app.data.model.AIChatRequest
import com.expenseflow.app.data.model.AIChatResponse
import com.expenseflow.app.data.model.AIRecommendationResponse
import com.expenseflow.app.data.model.Budget50_30_20
import com.expenseflow.app.data.model.SubscriptionAuditResponse
import com.expenseflow.app.data.remote.AIApi
import com.expenseflow.app.di.IoDispatcher
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AIRepository @Inject constructor(
    private val aiApi: AIApi,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {

    suspend fun getRecommendations(forceRefresh: Boolean = false): Result<AIRecommendationResponse> =
        withContext(ioDispatcher) {
            try {
                val response = if (forceRefresh) {
                    aiApi.refreshRecommendations()
                } else {
                    aiApi.getRecommendations()
                }
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(parseError(response.errorBody()?.string())))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun sendMessage(
        message: String,
        history: List<AIChatMessage> = emptyList()
    ): Result<AIChatResponse> = withContext(ioDispatcher) {
        try {
            val request = AIChatRequest(
                message = message,
                conversationHistory = history
            )
            val response = aiApi.chatWithAssistant(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getSubscriptionAudit(): Result<SubscriptionAuditResponse> = withContext(ioDispatcher) {
        try {
            val response = aiApi.getSubscriptionAudit()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun get503020Breakdown(): Result<Budget50_30_20> = withContext(ioDispatcher) {
        try {
            val response = aiApi.get503020Breakdown()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun parseError(errorBody: String?): String {
        if (errorBody.isNullOrBlank()) return "Failed to communicate with AI intelligence service"
        return try {
            val json = JSONObject(errorBody)
            when {
                json.has("detail") -> json.getString("detail")
                json.has("message") -> json.getString("message")
                else -> errorBody
            }
        } catch (_: Exception) {
            errorBody
        }
    }
}
