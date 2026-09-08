package com.expenseflow.app.data.remote

import com.expenseflow.app.data.model.DashboardSummaryResponse
import com.expenseflow.app.data.model.MonthlyAnalyticsResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface AnalyticsApi {

    @GET("analytics/monthly")
    suspend fun getMonthlyAnalytics(
        @Query("month") month: Int? = null,
        @Query("year") year: Int? = null
    ): Response<MonthlyAnalyticsResponse>

    @GET("dashboard/summary")
    suspend fun getDashboardSummary(): Response<DashboardSummaryResponse>
}
