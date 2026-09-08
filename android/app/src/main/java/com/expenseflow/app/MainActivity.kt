package com.expenseflow.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.expenseflow.app.data.local.SessionManager
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.navigation.ExpenseFlowNavGraph
import com.expenseflow.app.ui.theme.BackgroundDark
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
            ExpenseFlowTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = BackgroundDark
                ) {
                    ExpenseFlowNavGraph(
                        sessionManager = sessionManager,
                        authRepository = authRepository
                    )
                }
            }
        }
    }
}
