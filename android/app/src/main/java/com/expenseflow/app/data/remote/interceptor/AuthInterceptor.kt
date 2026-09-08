package com.expenseflow.app.data.remote.interceptor

import com.expenseflow.app.data.local.SessionManager
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthInterceptor @Inject constructor(
    private val sessionManager: SessionManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val builder = original.newBuilder()

        val token = sessionManager.getAccessToken()
        if (!token.isNullOrBlank()) {
            builder.header("Authorization", "Bearer $token")
        }

        // Add refresh token cookie if present as fallback
        val refreshToken = sessionManager.getRefreshToken()
        if (!refreshToken.isNullOrBlank() && original.header("Cookie") == null) {
            builder.header("Cookie", "refresh_token=$refreshToken")
        }

        return chain.proceed(builder.build())
    }
}
