package com.expenseflow.app.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.expenseflow.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class RegisterStep {
    EMAIL,
    OTP,
    PROFILE
}

data class RegisterUiState(
    val currentStep: RegisterStep = RegisterStep.EMAIL,
    val email: String = "",
    val otpDigits: List<String> = List(6) { "" },
    val verificationToken: String = "",
    val fullName: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val resendCooldown: Int = 0,
    val isCompleted: Boolean = false
) {
    val fullOtp: String get() = otpDigits.joinToString("")
    val isOtpComplete: Boolean get() = otpDigits.all { it.isNotBlank() }
}

@HiltViewModel
class RegisterViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState: StateFlow<RegisterUiState> = _uiState.asStateFlow()

    private var timerJob: Job? = null

    fun onEmailChange(email: String) {
        _uiState.value = _uiState.value.copy(email = email, errorMessage = null)
    }

    fun onOtpDigitChange(index: Int, digit: String) {
        if (digit.length > 1) {
            // Handle paste of 6 digits
            val clean = digit.filter { it.isDigit() }
            if (clean.length == 6) {
                val newDigits = clean.map { it.toString() }
                _uiState.value = _uiState.value.copy(otpDigits = newDigits, errorMessage = null)
                return
            }
        }
        val current = _uiState.value.otpDigits.toMutableList()
        current[index] = digit.takeLast(1)
        _uiState.value = _uiState.value.copy(otpDigits = current, errorMessage = null)
    }

    fun onFullNameChange(fullName: String) {
        _uiState.value = _uiState.value.copy(fullName = fullName, errorMessage = null)
    }

    fun onPasswordChange(password: String) {
        _uiState.value = _uiState.value.copy(password = password, errorMessage = null)
    }

    fun onConfirmPasswordChange(confirm: String) {
        _uiState.value = _uiState.value.copy(confirmPassword = confirm, errorMessage = null)
    }

    fun sendOtp() {
        val email = _uiState.value.email.trim()
        if (email.isBlank() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            _uiState.value = _uiState.value.copy(errorMessage = "Please enter a valid email address")
            return
        }

        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

        viewModelScope.launch {
            val result = authRepository.sendRegistrationOtp(email)
            result.onSuccess {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    currentStep = RegisterStep.OTP
                )
                startCooldown(60)
            }.onFailure { error ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = error.message ?: "Failed to send verification OTP"
                )
            }
        }
    }

    fun resendOtp() {
        if (_uiState.value.resendCooldown > 0 || _uiState.value.isLoading) return
        sendOtp()
    }

    fun verifyOtp() {
        val state = _uiState.value
        val otp = state.fullOtp
        if (otp.length != 6) {
            _uiState.value = state.copy(errorMessage = "Please enter all 6 digits of the OTP")
            return
        }

        _uiState.value = state.copy(isLoading = true, errorMessage = null)

        viewModelScope.launch {
            val result = authRepository.verifyRegistrationOtp(state.email, otp)
            result.onSuccess { response ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    verificationToken = response.verificationToken,
                    currentStep = RegisterStep.PROFILE
                )
            }.onFailure { error ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = error.message ?: "Invalid or expired OTP code"
                )
            }
        }
    }

    fun completeRegistration() {
        val state = _uiState.value
        if (state.password.length < 8) {
            _uiState.value = state.copy(errorMessage = "Password must be at least 8 characters")
            return
        }
        if (state.password != state.confirmPassword) {
            _uiState.value = state.copy(errorMessage = "Passwords do not match")
            return
        }

        _uiState.value = state.copy(isLoading = true, errorMessage = null)

        viewModelScope.launch {
            val result = authRepository.completeRegistration(
                email = state.email,
                verificationToken = state.verificationToken,
                fullName = state.fullName,
                password = state.password
            )
            result.onSuccess {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isCompleted = true
                )
            }.onFailure { error ->
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = error.message ?: "Failed to complete account registration"
                )
            }
        }
    }

    private fun startCooldown(seconds: Int) {
        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            for (i in seconds downTo 1) {
                _uiState.value = _uiState.value.copy(resendCooldown = i)
                delay(1000)
            }
            _uiState.value = _uiState.value.copy(resendCooldown = 0)
        }
    }
}
