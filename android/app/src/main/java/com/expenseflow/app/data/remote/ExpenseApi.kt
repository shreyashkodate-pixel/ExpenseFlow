package com.expenseflow.app.data.remote

import com.expenseflow.app.data.model.CategoryCreateRequest
import com.expenseflow.app.data.model.CategoryDto
import com.expenseflow.app.data.model.ExpenseCreateRequest
import com.expenseflow.app.data.model.ExpenseDto
import com.expenseflow.app.data.model.ExpenseUpdateRequest
import com.expenseflow.app.data.model.PaginatedExpensesResponse
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query
import retrofit2.http.Streaming

interface ExpenseApi {

    @GET("expenses")
    suspend fun getExpenses(
        @Query("search") search: String? = null,
        @Query("category_id") categoryId: Int? = null,
        @Query("payment_method") paymentMethod: String? = null,
        @Query("amount_min") amountMin: Double? = null,
        @Query("amount_max") amountMax: Double? = null,
        @Query("date_from") dateFrom: String? = null,
        @Query("date_to") dateTo: String? = null,
        @Query("sort") sort: String = "date",
        @Query("order") order: String = "desc",
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 50
    ): Response<PaginatedExpensesResponse>

    @POST("expenses")
    suspend fun createExpense(
        @Body request: ExpenseCreateRequest
    ): Response<ExpenseDto>

    @GET("expenses/{id}")
    suspend fun getExpenseById(
        @Path("id") id: Int
    ): Response<ExpenseDto>

    @PUT("expenses/{id}")
    suspend fun updateExpense(
        @Path("id") id: Int,
        @Body request: ExpenseUpdateRequest
    ): Response<ExpenseDto>

    @DELETE("expenses/{id}")
    suspend fun deleteExpense(
        @Path("id") id: Int
    ): Response<Unit>

    @GET("categories")
    suspend fun getCategories(): Response<List<CategoryDto>>

    @POST("categories")
    suspend fun createCategory(
        @Body request: CategoryCreateRequest
    ): Response<CategoryDto>

    @Streaming
    @GET("expenses/export")
    suspend fun exportExpenses(
        @Query("format") format: String = "pdf"
    ): Response<ResponseBody>
}
