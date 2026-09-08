package com.expenseflow.app.di

import com.expenseflow.app.BuildConfig
import com.expenseflow.app.data.remote.AuthApi
import com.expenseflow.app.data.remote.interceptor.AuthInterceptor
import com.expenseflow.app.data.remote.interceptor.TokenAuthenticator
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideJson(): Json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
        isLenient = true
        encodeDefaults = true
    }

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        tokenAuthenticator: TokenAuthenticator,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(authInterceptor)
            .authenticator(tokenAuthenticator)
            .addInterceptor(loggingInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        json: Json
    ): Retrofit {
        val contentType = "application/json".toMediaType()
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }

    @Provides
    @Singleton
    fun provideExpenseApi(retrofit: Retrofit): com.expenseflow.app.data.remote.ExpenseApi {
        return retrofit.create(com.expenseflow.app.data.remote.ExpenseApi::class.java)
    }

    @Provides
    @Singleton
    fun provideBudgetApi(retrofit: Retrofit): com.expenseflow.app.data.remote.BudgetApi {
        return retrofit.create(com.expenseflow.app.data.remote.BudgetApi::class.java)
    }

    @Provides
    @Singleton
    fun provideAnalyticsApi(retrofit: Retrofit): com.expenseflow.app.data.remote.AnalyticsApi {
        return retrofit.create(com.expenseflow.app.data.remote.AnalyticsApi::class.java)
    }

    @Provides
    @Singleton
    fun provideAIApi(retrofit: Retrofit): com.expenseflow.app.data.remote.AIApi {
        return retrofit.create(com.expenseflow.app.data.remote.AIApi::class.java)
    }
}
