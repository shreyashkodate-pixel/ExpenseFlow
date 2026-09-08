package com.expenseflow.app.data.remote

import com.expenseflow.app.data.model.AIChatRequest
import com.expenseflow.app.data.model.AIChatResponse
import com.expenseflow.app.data.model.AIRecommendationResponse
import com.expenseflow.app.data.model.Budget50_30_20
import com.expenseflow.app.data.model.SubscriptionAuditResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AIApi {

    @GET("ai/recommendations")
    suspend fun getRecommendations(): Response<AIRecommendationResponse>

    @POST("ai/recommendations/refresh")
    suspend fun refreshRecommendations(): Response<AIRecommendationResponse>

    @POST("ai/chat")
    suspend fun chatWithAssistant(
        @Body request: AIChatRequest
    ): Response<AIChatResponse>

    @GET("ai/subscriptions")
    suspend fun getSubscriptionAudit(): Response<SubscriptionAuditResponse>

    @GET("ai/50-30-20")
    suspend fun get503020Breakdown(): Response<Budget50_30_20>
}
