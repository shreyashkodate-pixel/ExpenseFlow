package com.expenseflow.app.presentation.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.expenseflow.app.presentation.components.ExpenseInputField
import com.expenseflow.app.presentation.components.GlassCard
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.ui.theme.AccentEmerald
import com.expenseflow.app.ui.theme.BackgroundDark
import com.expenseflow.app.ui.theme.BorderDark
import com.expenseflow.app.ui.theme.ErrorRose
import com.expenseflow.app.ui.theme.PrimaryViolet
import com.expenseflow.app.ui.theme.SurfaceDark
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import com.expenseflow.app.ui.theme.WarningAmber

@Composable
fun RegisterScreen(
    viewModel: RegisterViewModel,
    onNavigateToLogin: (String?) -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    var passwordVisible by remember { mutableStateOf(false) }

    LaunchedEffect(uiState.isCompleted) {
        if (uiState.isCompleted) {
            onNavigateToLogin("Registration successful! Please sign in with your credentials.")
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Spacer(modifier = Modifier.height(32.dp))

        // Branding
        Text(
            text = "ExpenseFlow",
            style = MaterialTheme.typography.displayMedium,
            color = PrimaryViolet,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = "Create your secure account",
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )

        Spacer(modifier = Modifier.height(28.dp))

        // 3-Step Wizard Progress Bar
        StepIndicator(currentStep = uiState.currentStep)

        Spacer(modifier = Modifier.height(28.dp))

        // Multi-Step Form Card
        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                when (uiState.currentStep) {
                    RegisterStep.EMAIL -> {
                        Text(
                            text = "Step 1: Verify Email",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TextPrimary
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "We'll send a 6-digit verification code to confirm your email.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        Spacer(modifier = Modifier.height(20.dp))

                        ExpenseInputField(
                            value = uiState.email,
                            onValueChange = viewModel::onEmailChange,
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

                        if (uiState.errorMessage != null) {
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                text = uiState.errorMessage!!,
                                style = MaterialTheme.typography.bodySmall,
                                color = ErrorRose
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        PrimaryButton(
                            text = "Send Verification Code",
                            onClick = viewModel::sendOtp,
                            isLoading = uiState.isLoading
                        )
                    }

                    RegisterStep.OTP -> {
                        Text(
                            text = "Step 2: Enter OTP",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TextPrimary
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "Enter the 6-digit code sent to ${uiState.email}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextSecondary
                        )
                        Spacer(modifier = Modifier.height(24.dp))

                        // 6 Digit OTP Boxes
                        OtpInputBoxes(
                            digits = uiState.otpDigits,
                            onDigitChange = viewModel::onOtpDigitChange
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        // Cooldown / Resend
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Center
                        ) {
                            if (uiState.resendCooldown > 0) {
                                Text(
                                    text = "Resend code in ${uiState.resendCooldown}s",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = TextMuted
                                )
                            } else {
                                Text(
                                    text = "Didn't receive code? Resend",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = PrimaryViolet,
                                    modifier = Modifier.clickable { viewModel.resendOtp() }
                                )
                            }
                        }

                        if (uiState.errorMessage != null) {
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                text = uiState.errorMessage!!,
                                style = MaterialTheme.typography.bodySmall,
                                color = ErrorRose
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        PrimaryButton(
                            text = "Verify Code",
                            onClick = viewModel::verifyOtp,
                            isLoading = uiState.isLoading,
                            enabled = uiState.isOtpComplete
                        )
                    }

                    RegisterStep.PROFILE -> {
                        Text(
                            text = "Step 3: Complete Profile",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TextPrimary
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "Email verified! Set up your name and password.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = AccentEmerald
                        )
                        Spacer(modifier = Modifier.height(20.dp))

                        ExpenseInputField(
                            value = uiState.fullName,
                            onValueChange = viewModel::onFullNameChange,
                            label = "Full Name (Optional)",
                            placeholder = "John Doe",
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Default.Person,
                                    contentDescription = "Name",
                                    tint = TextMuted
                                )
                            },
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next)
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        ExpenseInputField(
                            value = uiState.password,
                            onValueChange = viewModel::onPasswordChange,
                            label = "Create Password",
                            placeholder = "At least 8 characters",
                            visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Default.Lock,
                                    contentDescription = "Password",
                                    tint = TextMuted
                                )
                            },
                            trailingIcon = {
                                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                    Icon(
                                        imageVector = if (passwordVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                        contentDescription = "Toggle password",
                                        tint = TextMuted
                                    )
                                }
                            },
                            keyboardOptions = KeyboardOptions(
                                keyboardType = KeyboardType.Password,
                                imeAction = ImeAction.Next
                            )
                        )

                        // Password strength indicator
                        if (uiState.password.isNotBlank()) {
                            Spacer(modifier = Modifier.height(8.dp))
                            val (strengthText, strengthColor) = when {
                                uiState.password.length < 8 -> Pair("Too short (min 8 chars)", ErrorRose)
                                uiState.password.any { it.isDigit() } && uiState.password.any { !it.isLetterOrDigit() } -> Pair("Strong Password", AccentEmerald)
                                else -> Pair("Good Password", WarningAmber)
                            }
                            Text(
                                text = "Strength: $strengthText",
                                style = MaterialTheme.typography.bodySmall,
                                color = strengthColor
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        ExpenseInputField(
                            value = uiState.confirmPassword,
                            onValueChange = viewModel::onConfirmPasswordChange,
                            label = "Confirm Password",
                            placeholder = "Repeat password",
                            visualTransformation = PasswordVisualTransformation(),
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Default.Lock,
                                    contentDescription = "Confirm Password",
                                    tint = TextMuted
                                )
                            },
                            keyboardOptions = KeyboardOptions(
                                keyboardType = KeyboardType.Password,
                                imeAction = ImeAction.Done
                            )
                        )

                        if (uiState.errorMessage != null) {
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                text = uiState.errorMessage!!,
                                style = MaterialTheme.typography.bodySmall,
                                color = ErrorRose
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        PrimaryButton(
                            text = "Complete Registration",
                            onClick = viewModel::completeRegistration,
                            isLoading = uiState.isLoading
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Navigate to Login
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Text(
                text = "Already have an account? ",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
            Text(
                text = "Sign In",
                style = MaterialTheme.typography.titleMedium,
                color = PrimaryViolet,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.clickable { onNavigateToLogin(null) }
            )
        }

        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
private fun StepIndicator(currentStep: RegisterStep) {
    val steps = listOf("Email", "Verify OTP", "Profile")
    val currentIdx = currentStep.ordinal

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        steps.forEachIndexed { index, title ->
            val isActive = index <= currentIdx
            val isCurrent = index == currentIdx

            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .background(
                            if (isActive) PrimaryViolet else SurfaceDark,
                            shape = CircleShape
                        )
                        .border(
                            1.dp,
                            if (isCurrent) PrimaryViolet else BorderDark,
                            shape = CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "${index + 1}",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (isActive) Color.White else TextMuted,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isActive) TextPrimary else TextMuted
                )
            }

            if (index < steps.size - 1) {
                Spacer(modifier = Modifier.width(8.dp))
                Box(
                    modifier = Modifier
                        .width(20.dp)
                        .height(1.dp)
                        .background(if (index < currentIdx) PrimaryViolet else BorderDark)
                )
                Spacer(modifier = Modifier.width(8.dp))
            }
        }
    }
}

@Composable
private fun OtpInputBoxes(
    digits: List<String>,
    onDigitChange: (Int, String) -> Unit
) {
    val focusRequesters = remember { List(6) { FocusRequester() } }

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        digits.forEachIndexed { index, digit ->
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .background(SurfaceDark, shape = RoundedCornerShape(10.dp))
                    .border(
                        1.5.dp,
                        if (digit.isNotEmpty()) PrimaryViolet else BorderDark,
                        shape = RoundedCornerShape(10.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                BasicTextField(
                    value = digit,
                    onValueChange = { newText ->
                        onDigitChange(index, newText)
                        if (newText.isNotEmpty() && index < 5) {
                            focusRequesters[index + 1].requestFocus()
                        }
                    },
                    modifier = Modifier
                        .focusRequester(focusRequesters[index])
                        .fillMaxWidth(),
                    textStyle = TextStyle(
                        color = TextPrimary,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center
                    ),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number,
                        imeAction = if (index == 5) ImeAction.Done else ImeAction.Next
                    ),
                    cursorBrush = SolidColor(PrimaryViolet),
                    singleLine = true
                )
            }
        }
    }
}
