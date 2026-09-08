package com.expenseflow.app.data.remote.interceptor

import com.expenseflow.app.BuildConfig
import com.expenseflow.app.data.local.SessionManager
import com.expenseflow.app.data.model.TokenResponse
import kotlinx.serialization.json.Json
import okhttp3.Authenticator
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.Route
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TokenAuthenticator @Inject constructor(
    private val sessionManager: SessionManager
) : Authenticator {

    private val json = Json { ignoreUnknownKeys = true }

    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent infinite loops on repeated 401s
        if (responseCount(response) >= 3) {
            sessionManager.clearSession()
            return null
        }

        val currentRefreshToken = sessionManager.getRefreshToken() ?: run {
            sessionManager.clearSession()
            return null
        }

        // Execute synchronous refresh call
        synchronized(this) {
            val latestToken = sessionManager.getAccessToken()
            val requestToken = response.request.header("Authorization")?.removePrefix("Bearer ")

            // If another thread already refreshed the token, simply retry with the latest token
            if (latestToken != null && latestToken != requestToken) {
                return response.request.newBuilder()
                    .header("Authorization", "Bearer $latestToken")
                    .build()
            }

            val refreshUrl = BuildConfig.BASE_URL + "auth/refresh"
            val body = """{"refresh_token":"$currentRefreshToken"}"""
                .toRequestBody("application/json".toMediaType())

            val refreshRequest = Request.Builder()
                .url(refreshUrl)
                .post(body)
                .header("Cookie", "refresh_token=$currentRefreshToken")
                .build()

            val client = OkHttpClient()
            try {
                val refreshResponse = client.newCall(refreshRequest).execute()
                if (refreshResponse.isSuccessful) {
                    val responseBody = refreshResponse.body?.string() ?: return null
                    val tokenData = json.decodeFromString<TokenResponse>(responseBody)

                    // Extract new refresh token from cookie or body
                    val newCookie = refreshResponse.headers("Set-Cookie")
                        .firstOrNull { it.startsWith("refresh_token=") }
                        ?.substringAfter("refresh_token=")
                        ?.substringBefore(";")

                    sessionManager.saveTokens(
                        accessToken = tokenData.accessToken,
                        refreshToken = newCookie ?: currentRefreshToken
                    )
                    sessionManager.saveUser(tokenData.user)

                    return response.request.newBuilder()
                        .header("Authorization", "Bearer ${tokenData.accessToken}")
                        .build()
                } else {
                    sessionManager.clearSession()
                    return null
                }
            } catch (_: Exception) {
                sessionManager.clearSession()
                return null
            }
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}
