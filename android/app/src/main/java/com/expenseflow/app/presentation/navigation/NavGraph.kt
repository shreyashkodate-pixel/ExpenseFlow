package com.expenseflow.app.presentation.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.expenseflow.app.data.local.SessionManager
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.auth.ForgotPasswordScreen
import com.expenseflow.app.presentation.auth.LoginScreen
import com.expenseflow.app.presentation.auth.LoginViewModel
import com.expenseflow.app.presentation.auth.RegisterScreen
import com.expenseflow.app.presentation.auth.RegisterViewModel
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.BackgroundDark
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import kotlinx.coroutines.launch

object Destinations {
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val FORGOT_PASSWORD = "forgot_password"
    const val MAIN = "main"
}

@Composable
fun ExpenseFlowNavGraph(
    navController: NavHostController = rememberNavController(),
    sessionManager: SessionManager,
    authRepository: AuthRepository
) {
    val isLoggedIn by sessionManager.isLoggedIn.collectAsState()
    val startDestination = if (isLoggedIn) Destinations.MAIN else Destinations.LOGIN

    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(
            route = "${Destinations.LOGIN}?registered={registered}&msg={msg}",
            arguments = listOf(
                navArgument("registered") {
                    type = NavType.BoolType
                    defaultValue = false
                },
                navArgument("msg") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val loginViewModel: LoginViewModel = hiltViewModel()
            val msg = backStackEntry.arguments?.getString("msg")

            LoginScreen(
                viewModel = loginViewModel,
                registrationMessage = msg,
                onNavigateToRegister = {
                    navController.navigate(Destinations.REGISTER)
                },
                onNavigateToForgotPassword = {
                    navController.navigate(Destinations.FORGOT_PASSWORD)
                },
                onLoginSuccess = {
                    navController.navigate(Destinations.MAIN) {
                        popUpTo(Destinations.LOGIN) { inclusive = true }
                    }
                }
            )
        }

        composable(Destinations.REGISTER) {
            val registerViewModel: RegisterViewModel = hiltViewModel()
            RegisterScreen(
                viewModel = registerViewModel,
                onNavigateToLogin = { successMsg ->
                    if (successMsg != null) {
                        navController.navigate("${Destinations.LOGIN}?registered=true&msg=$successMsg") {
                            popUpTo(Destinations.REGISTER) { inclusive = true }
                        }
                    } else {
                        navController.popBackStack()
                    }
                }
            )
        }

        composable(Destinations.FORGOT_PASSWORD) {
            ForgotPasswordScreen(
                authRepository = authRepository,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.MAIN) {
            com.expenseflow.app.presentation.main.MainScreen(
                authRepository = authRepository,
                onLogout = {
                    navController.navigate(Destinations.LOGIN) {
                        popUpTo(Destinations.MAIN) { inclusive = true }
                    }
                }
            )
        }
    }
}
