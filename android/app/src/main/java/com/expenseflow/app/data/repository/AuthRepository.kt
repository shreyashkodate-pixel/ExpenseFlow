package com.expenseflow.app.data.repository

import com.expenseflow.app.data.local.SessionManager
import com.expenseflow.app.data.model.CompleteRegistrationRequest
import com.expenseflow.app.data.model.CompleteRegistrationResponse
import com.expenseflow.app.data.model.ForgotPasswordRequest
import com.expenseflow.app.data.model.LoginRequest
import com.expenseflow.app.data.model.ResetPasswordRequest
import com.expenseflow.app.data.model.SendOtpRequest
import com.expenseflow.app.data.model.SendOtpResponse
import com.expenseflow.app.data.model.TokenResponse
import com.expenseflow.app.data.model.UserDto
import com.expenseflow.app.data.model.VerifyOtpRequest
import com.expenseflow.app.data.model.VerifyOtpResponse
import com.expenseflow.app.data.remote.AuthApi
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val sessionManager: SessionManager
) {
    val isLoggedIn: StateFlow<Boolean> = sessionManager.isLoggedIn

    fun getCurrentUser(): UserDto? = sessionManager.getUser()

    suspend fun sendRegistrationOtp(email: String): Result<SendOtpResponse> {
        return try {
            val response = authApi.sendRegistrationOtp(SendOtpRequest(email = email.trim()))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun verifyRegistrationOtp(email: String, otp: String): Result<VerifyOtpResponse> {
        return try {
            val response = authApi.verifyRegistrationOtp(
                VerifyOtpRequest(email = email.trim(), otp = otp.trim())
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun completeRegistration(
        email: String,
        verificationToken: String,
        fullName: String?,
        password: String
    ): Result<CompleteRegistrationResponse> {
        return try {
            val response = authApi.completeRegistration(
                CompleteRegistrationRequest(
                    email = email.trim(),
                    verificationToken = verificationToken,
                    fullName = fullName?.trim()?.ifBlank { null },
                    password = password
                )
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun login(email: String, password: String): Result<TokenResponse> {
        return try {
            val response = authApi.login(LoginRequest(email = email.trim(), password = password))
            if (response.isSuccessful && response.body() != null) {
                val tokenData = response.body()!!

                // Extract refresh token from Set-Cookie header if present
                val refreshCookie = response.headers().values("Set-Cookie")
                    .firstOrNull { it.startsWith("refresh_token=") }
                    ?.substringAfter("refresh_token=")
                    ?.substringBefore(";")

                sessionManager.saveTokens(
                    accessToken = tokenData.accessToken,
                    refreshToken = refreshCookie
                )
                sessionManager.saveUser(tokenData.user)

                Result.success(tokenData)
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun forgotPassword(email: String): Result<String> {
        return try {
            val response = authApi.forgotPassword(ForgotPasswordRequest(email = email.trim()))
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Password reset instructions sent to your email.")
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun resetPassword(token: String, newPassword: String): Result<String> {
        return try {
            val response = authApi.resetPassword(ResetPasswordRequest(token = token, newPassword = newPassword))
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Password reset successfully. Please sign in.")
            } else {
                Result.failure(Exception(parseErrorMessage(response.errorBody()?.string())))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout() {
        try {
            authApi.logout()
        } catch (_: Exception) {}
        sessionManager.clearSession()
    }

    private fun parseErrorMessage(errorBody: String?): String {
        if (errorBody.isNullOrBlank()) return "An unexpected error occurred. Please try again."
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
