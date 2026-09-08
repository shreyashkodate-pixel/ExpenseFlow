package com.expenseflow.app.data.remote

import com.expenseflow.app.data.model.CompleteRegistrationRequest
import com.expenseflow.app.data.model.CompleteRegistrationResponse
import com.expenseflow.app.data.model.ForgotPasswordRequest
import com.expenseflow.app.data.model.LoginRequest
import com.expenseflow.app.data.model.MessageResponse
import com.expenseflow.app.data.model.RefreshTokenRequest
import com.expenseflow.app.data.model.ResetPasswordRequest
import com.expenseflow.app.data.model.SendOtpRequest
import com.expenseflow.app.data.model.SendOtpResponse
import com.expenseflow.app.data.model.TokenResponse
import com.expenseflow.app.data.model.UserDto
import com.expenseflow.app.data.model.VerifyOtpRequest
import com.expenseflow.app.data.model.VerifyOtpResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {

    @POST("auth/register/send-otp")
    suspend fun sendRegistrationOtp(
        @Body request: SendOtpRequest
    ): Response<SendOtpResponse>

    @POST("auth/register/verify-otp")
    suspend fun verifyRegistrationOtp(
        @Body request: VerifyOtpRequest
    ): Response<VerifyOtpResponse>

    @POST("auth/register/complete")
    suspend fun completeRegistration(
        @Body request: CompleteRegistrationRequest
    ): Response<CompleteRegistrationResponse>

    @POST("auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<TokenResponse>

    @POST("auth/refresh")
    suspend fun refreshToken(
        @Body request: RefreshTokenRequest
    ): Response<TokenResponse>

    @GET("auth/me")
    suspend fun getCurrentUser(): Response<UserDto>

    @POST("auth/logout")
    suspend fun logout(): Response<MessageResponse>

    @POST("auth/forgot-password")
    suspend fun forgotPassword(
        @Body request: ForgotPasswordRequest
    ): Response<MessageResponse>

    @POST("auth/reset-password")
    suspend fun resetPassword(
        @Body request: ResetPasswordRequest
    ): Response<MessageResponse>
}
