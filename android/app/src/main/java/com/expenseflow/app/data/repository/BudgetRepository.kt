package com.expenseflow.app.data.repository

import com.expenseflow.app.data.model.BudgetCreateRequest
import com.expenseflow.app.data.model.BudgetResponse
import com.expenseflow.app.data.model.OverallBudgetStatusResponse
import com.expenseflow.app.data.remote.BudgetApi
import com.expenseflow.app.di.IoDispatcher
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BudgetRepository @Inject constructor(
    private val budgetApi: BudgetApi,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {
    suspend fun getBudgetStatus(month: Int? = null, year: Int? = null): Result<OverallBudgetStatusResponse> =
        withContext(ioDispatcher) {
            try {
                val response = budgetApi.getBudgetStatus(month, year)
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(parseError(response.errorBody()?.string())))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun createOrUpdateBudget(
        month: Int,
        year: Int,
        amount: Double,
        categoryId: Int? = null
    ): Result<BudgetResponse> = withContext(ioDispatcher) {
        try {
            val request = BudgetCreateRequest(
                month = month,
                year = year,
                amount = amount,
                categoryId = categoryId
            )
            val response = budgetApi.createOrUpdateBudget(request)
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
        if (errorBody.isNullOrBlank()) return "Failed to communicate with budget service"
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
