package com.expenseflow.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.expenseflow.app.data.local.SessionManager
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.navigation.ExpenseFlowNavGraph
import com.expenseflow.app.ui.theme.ExpenseFlowTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val systemDark = isSystemInDarkTheme()
            var userDarkTheme by rememberSaveable { mutableStateOf<Boolean?>(null) }
            val isDark = userDarkTheme ?: false

            ExpenseFlowTheme(darkTheme = isDark) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ExpenseFlowNavGraph(
                        sessionManager = sessionManager,
                        authRepository = authRepository,
                        isDarkTheme = isDark,
                        onToggleTheme = {
                            userDarkTheme = !isDark
                        }
                    )
                }
            }
        }
    }
}
