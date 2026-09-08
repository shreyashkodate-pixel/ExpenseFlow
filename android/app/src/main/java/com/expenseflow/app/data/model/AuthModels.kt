package com.expenseflow.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SendOtpRequest(
    val email: String
)

@Serializable
data class SendOtpResponse(
    val status: String,
    val email: String,
    val message: String
)

@Serializable
data class VerifyOtpRequest(
    val email: String,
    val otp: String
)

@Serializable
data class VerifyOtpResponse(
    val status: String,
    val email: String,
    @SerialName("verification_token")
    val verificationToken: String,
    val message: String
)

@Serializable
data class CompleteRegistrationRequest(
    val email: String,
    @SerialName("verification_token")
    val verificationToken: String,
    @SerialName("full_name")
    val fullName: String? = null,
    val password: String
)

@Serializable
data class CompleteRegistrationResponse(
    val status: String,
    val message: String,
    val user: UserDto? = null
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String
)

@Serializable
data class TokenResponse(
    @SerialName("access_token")
    val accessToken: String,
    @SerialName("token_type")
    val tokenType: String = "bearer",
    val user: UserDto
)

@Serializable
data class RefreshTokenRequest(
    @SerialName("refresh_token")
    val refreshToken: String? = null
)

@Serializable
data class UserDto(
    val id: Int,
    val email: String,
    @SerialName("full_name")
    val fullName: String? = null,
    @SerialName("avatar_url")
    val avatarUrl: String? = null,
    @SerialName("is_verified")
    val isVerified: Boolean = false,
    @SerialName("created_at")
    val createdAt: String? = null
)

@Serializable
data class ForgotPasswordRequest(
    val email: String
)

@Serializable
data class ResetPasswordRequest(
    val token: String,
    @SerialName("new_password")
    val newPassword: String
)

@Serializable
data class MessageResponse(
    val message: String,
    val status: String? = null
)
