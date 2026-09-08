package com.expenseflow.app.di

import android.content.Context
import androidx.room.Room
import com.expenseflow.app.data.local.room.CategoryDao
import com.expenseflow.app.data.local.room.ExpenseDao
import com.expenseflow.app.data.local.room.ExpenseFlowDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideExpenseFlowDatabase(
        @ApplicationContext context: Context
    ): ExpenseFlowDatabase {
        return Room.databaseBuilder(
            context,
            ExpenseFlowDatabase::class.java,
            "expenseflow_local.db"
        ).fallbackToDestructiveMigration().build()
    }

    @Provides
    @Singleton
    fun provideExpenseDao(database: ExpenseFlowDatabase): ExpenseDao {
        return database.expenseDao()
    }

    @Provides
    @Singleton
    fun provideCategoryDao(database: ExpenseFlowDatabase): CategoryDao {
        return database.categoryDao()
    }
}
