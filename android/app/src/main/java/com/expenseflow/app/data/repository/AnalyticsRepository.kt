package com.expenseflow.app.data.repository

import com.expenseflow.app.data.model.DashboardSummaryResponse
import com.expenseflow.app.data.model.MonthlyAnalyticsResponse
import com.expenseflow.app.data.remote.AnalyticsApi
import com.expenseflow.app.di.IoDispatcher
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AnalyticsRepository @Inject constructor(
    private val analyticsApi: AnalyticsApi,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getMonthlyAnalytics(month: Int? = null, year: Int? = null): Result<MonthlyAnalyticsResponse> =
        withContext(ioDispatcher) {
            try {
                val response = analyticsApi.getMonthlyAnalytics(month, year)
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(parseError(response.errorBody()?.string())))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun getDashboardSummary(): Result<DashboardSummaryResponse> = withContext(ioDispatcher) {
        try {
            val response = analyticsApi.getDashboardSummary()
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
        if (errorBody.isNullOrBlank()) return "Failed to retrieve analytics data"
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
