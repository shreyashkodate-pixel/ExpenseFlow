package com.expenseflow.app.presentation.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Email
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.expenseflow.app.data.repository.AuthRepository
import com.expenseflow.app.presentation.components.BadgeStatus
import com.expenseflow.app.presentation.components.ExpenseInputField
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.presentation.components.StatusBadge
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.BackgroundDark
import com.expenseflow.app.ui.theme.ErrorRose
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import kotlinx.coroutines.launch

@Composable
fun ForgotPasswordScreen(
    authRepository: AuthRepository,
    onNavigateBack: () -> Unit
) {
    var email by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var successMessage by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        // Back button
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    tint = TextPrimary
                )
            }
            Text(
                text = "Back to Sign In",
                style = MaterialTheme.typography.titleMedium,
                color = TextSecondary,
                modifier = Modifier.clickable { onNavigateBack() }
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text(
                    text = "Reset Password",
                    style = MaterialTheme.typography.headlineSmall,
                    color = TextPrimary
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Enter your registered email address to receive password recovery instructions.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )

                Spacer(modifier = Modifier.height(24.dp))

                if (successMessage != null) {
                    GlassCard(
                        borderColor = AccentEmerald,
                        backgroundColor = BackgroundDark,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column {
                            StatusBadge(text = "EMAIL SENT", status = BadgeStatus.SAFE)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = successMessage!!,
                                style = MaterialTheme.typography.bodyMedium,
                                color = AccentEmerald
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                } else {
                    ExpenseInputField(
                        value = email,
                        onValueChange = {
                            email = it
                            errorMessage = null
                        },
                        label = "Email Address",
                        placeholder = "you@example.com",
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Default.Email,
                                contentDescription = "Email",
                                tint = TextMuted
                            )
                        },
                        keyboardOptions = KeyboardOptions(
                            keyboardType = KeyboardType.Email,
                            imeAction = ImeAction.Done
                        )
                    )

                    if (errorMessage != null) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = errorMessage!!,
                            style = MaterialTheme.typography.bodySmall,
                            color = ErrorRose
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    PrimaryButton(
                        text = "Send Recovery Email",
                        onClick = {
                            if (email.isBlank()) {
                                errorMessage = "Please enter your email"
                                return@PrimaryButton
                            }
                            isLoading = true
                            errorMessage = null
                            scope.launch {
                                val result = authRepository.forgotPassword(email)
                                isLoading = false
                                result.onSuccess { msg ->
                                    successMessage = msg
                                }.onFailure { err ->
                                    errorMessage = err.message ?: "Failed to send reset link"
                                }
                            }
                        },
                        isLoading = isLoading
                    )
                }
            }
        }
    }
}
