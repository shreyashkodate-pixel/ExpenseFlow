package com.expenseflow.app.data.repository

import android.content.Context
import android.os.Environment
import com.expenseflow.app.data.local.room.CategoryDao
import com.expenseflow.app.data.local.room.CategoryEntity
import com.expenseflow.app.data.local.room.ExpenseDao
import com.expenseflow.app.data.local.room.ExpenseEntity
import com.expenseflow.app.data.model.CategoryDto
import com.expenseflow.app.data.model.ExpenseCreateRequest
import com.expenseflow.app.data.model.ExpenseDto
import com.expenseflow.app.data.remote.ExpenseApi
import com.expenseflow.app.di.IoDispatcher
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ExpenseRepository @Inject constructor(
    private val expenseApi: ExpenseApi,
    private val expenseDao: ExpenseDao,
    private val categoryDao: CategoryDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
    @ApplicationContext private val context: Context
) {
    val localExpenses: Flow<List<ExpenseEntity>> = expenseDao.getAllExpenses()
    val localCategories: Flow<List<CategoryEntity>> = categoryDao.getAllCategories()

    suspend fun refreshCategories(): Result<List<CategoryDto>> = withContext(ioDispatcher) {
        try {
            val response = expenseApi.getCategories()
            if (response.isSuccessful && response.body() != null) {
                val categories = response.body()!!
                val entities = categories.map { dto ->
                    CategoryEntity(
                        id = dto.id,
                        name = dto.name,
                        expenseCount = dto.expenseCount
                    )
                }
                categoryDao.insertAll(entities)
                Result.success(categories)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun refreshExpenses(
        search: String? = null,
        categoryId: Int? = null,
        paymentMethod: String? = null,
        dateFrom: String? = null,
        dateTo: String? = null
    ): Result<List<ExpenseDto>> = withContext(ioDispatcher) {
        try {
            val response = expenseApi.getExpenses(
                search = search?.ifBlank { null },
                categoryId = categoryId,
                paymentMethod = paymentMethod?.ifBlank { null },
                dateFrom = dateFrom?.ifBlank { null },
                dateTo = dateTo?.ifBlank { null },
                pageSize = 100
            )
            if (response.isSuccessful && response.body() != null) {
                val items = response.body()!!.items
                val entities = items.map { dto ->
                    ExpenseEntity(
                        id = dto.id,
                        amount = dto.amount,
                        categoryId = dto.categoryId,
                        categoryName = dto.category?.name ?: "General",
                        description = dto.description,
                        notes = dto.notes,
                        date = dto.date,
                        paymentMethod = dto.paymentMethod,
                        createdAt = dto.createdAt
                    )
                }
                expenseDao.insertAll(entities)
                Result.success(items)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createExpense(
        amount: Double,
        categoryId: Int,
        description: String,
        notes: String?,
        date: String,
        paymentMethod: String?
    ): Result<ExpenseDto> = withContext(ioDispatcher) {
        try {
            val request = ExpenseCreateRequest(
                amount = amount,
                categoryId = categoryId,
                description = description.trim(),
                notes = notes?.trim()?.ifBlank { null },
                date = date,
                paymentMethod = paymentMethod?.trim()?.ifBlank { null }
            )
            val response = expenseApi.createExpense(request)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                expenseDao.insert(
                    ExpenseEntity(
                        id = dto.id,
                        amount = dto.amount,
                        categoryId = dto.categoryId,
                        categoryName = dto.category?.name ?: "General",
                        description = dto.description,
                        notes = dto.notes,
                        date = dto.date,
                        paymentMethod = dto.paymentMethod,
                        createdAt = dto.createdAt
                    )
                )
                Result.success(dto)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteExpense(id: Int): Result<Unit> = withContext(ioDispatcher) {
        try {
            val response = expenseApi.deleteExpense(id)
            if (response.isSuccessful) {
                expenseDao.deleteById(id)
                Result.success(Unit)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun exportExpenses(format: String = "pdf"): Result<File> = withContext(ioDispatcher) {
        try {
            val response = expenseApi.exportExpenses(format.lowercase())
            if (response.isSuccessful && response.body() != null) {
                val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                if (!downloadsDir.exists()) {
                    downloadsDir.mkdirs()
                }
                val fileName = "ExpenseFlow_Report_${System.currentTimeMillis()}.${format.lowercase()}"
                val targetFile = File(downloadsDir, fileName)

                response.body()!!.byteStream().use { input ->
                    FileOutputStream(targetFile).use { output ->
                        input.copyTo(output)
                    }
                }
                Result.success(targetFile)
            } else {
                Result.failure(Exception(parseError(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun parseError(errorBody: String?): String {
        if (errorBody.isNullOrBlank()) return "An error occurred while managing expenses"
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
