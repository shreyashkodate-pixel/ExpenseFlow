package com.expenseflow.app.data.remote

import com.expenseflow.app.data.model.BudgetCreateRequest
import com.expenseflow.app.data.model.BudgetResponse
import com.expenseflow.app.data.model.OverallBudgetStatusResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface BudgetApi {

    @GET("budgets/status")
    suspend fun getBudgetStatus(
        @Query("month") month: Int? = null,
        @Query("year") year: Int? = null
    ): Response<OverallBudgetStatusResponse>

    @POST("budgets")
    suspend fun createOrUpdateBudget(
        @Body request: BudgetCreateRequest
    ): Response<BudgetResponse>

    @GET("budgets")
    suspend fun getBudgets(
        @Query("month") month: Int? = null,
        @Query("year") year: Int? = null,
        @Query("category_id") categoryId: Int? = null
    ): Response<List<BudgetResponse>>
}
