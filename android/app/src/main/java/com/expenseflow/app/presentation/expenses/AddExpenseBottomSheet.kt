package com.expenseflow.app.presentation.expenses

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableDoubleStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.expenseflow.app.data.local.room.CategoryEntity
import com.expenseflow.app.presentation.components.ExpenseInputField
import com.expenseflow.app.presentation.components.PrimaryButton
import com.expenseflow.app.ui.theme.BorderDark
import com.expenseflow.app.ui.theme.ErrorRose
import com.expenseflow.app.ui.theme.PrimaryContainer
import com.expenseflow.app.ui.theme.SurfaceCard
import com.expenseflow.app.ui.theme.SurfaceDark
import com.expenseflow.app.ui.theme.TextMuted
import com.expenseflow.app.ui.theme.TextPrimary
import com.expenseflow.app.ui.theme.TextSecondary
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddExpenseBottomSheet(
    categories: List<CategoryEntity>,
    onDismiss: () -> Unit,
    onSubmit: (amount: Double, categoryId: Int, description: String, notes: String?, date: String, paymentMethod: String?) -> Unit,
    isLoading: Boolean = false
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    var amountText by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }
    var selectedCategoryId by remember { mutableIntStateOf(categories.firstOrNull()?.id ?: 1) }

    val paymentMethods = listOf("GPay", "UPI", "Cash", "Credit Card", "Bank Transfer", "Others")
    var selectedPaymentMethod by remember { mutableStateOf(paymentMethods.first()) }

    val todayDate = remember {
        SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())
    }
    var expenseDate by remember { mutableStateOf(todayDate) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = MaterialTheme.colorScheme.surface
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text(
                text = "Add New Expense",
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Amount Input
            ExpenseInputField(
                value = amountText,
                onValueChange = {
                    if (it.isEmpty() || it.matches(Regex("^\\d*\\.?\\d{0,2}$"))) {
                        amountText = it
                        errorMessage = null
                    }
                },
                label = "Amount (₹)",
                placeholder = "0.00",
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Decimal,
                    imeAction = ImeAction.Next
                )
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Description Input
            ExpenseInputField(
                value = description,
                onValueChange = {
                    description = it
                    errorMessage = null
                },
                label = "Description",
                placeholder = "e.g. Grocery shopping, Uber ride",
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Category Chips Selector (Design.md Pill Chips)
            Text(
                text = "Category",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                categories.forEach { category ->
                    val isSelected = category.id == selectedCategoryId
                    Box(
                        modifier = Modifier
                            .background(
                                if (isSelected) PrimaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                                shape = RoundedCornerShape(20.dp)
                            )
                            .border(
                                1.dp,
                                if (isSelected) PrimaryContainer else MaterialTheme.colorScheme.outlineVariant,
                                shape = RoundedCornerShape(20.dp)
                            )
                            .clickable { selectedCategoryId = category.id }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = category.name,
                            style = MaterialTheme.typography.labelMedium,
                            color = if (isSelected) Color.White else MaterialTheme.colorScheme.onSurface,
                            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Payment Method Selector (Design.md Pill Chips)
            Text(
                text = "Payment Method",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                paymentMethods.forEach { method ->
                    val isSelected = method == selectedPaymentMethod
                    Box(
                        modifier = Modifier
                            .background(
                                if (isSelected) PrimaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                                shape = RoundedCornerShape(20.dp)
                            )
                            .border(
                                1.dp,
                                if (isSelected) PrimaryContainer else MaterialTheme.colorScheme.outlineVariant,
                                shape = RoundedCornerShape(20.dp)
                            )
                            .clickable { selectedPaymentMethod = method }
                            .padding(horizontal = 12.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = method,
                            style = MaterialTheme.typography.labelMedium,
                            color = if (isSelected) Color.White else MaterialTheme.colorScheme.onSurface,
                            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Date Input
            ExpenseInputField(
                value = expenseDate,
                onValueChange = { expenseDate = it },
                label = "Date (YYYY-MM-DD)",
                placeholder = todayDate,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Notes Input (Optional)
            ExpenseInputField(
                value = notes,
                onValueChange = { notes = it },
                label = "Notes (Optional)",
                placeholder = "Additional details...",
                singleLine = false,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done)
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
                text = "Save Expense",
                onClick = {
                    val amt = amountText.toDoubleOrNull()
                    if (amt == null || amt <= 0.0) {
                        errorMessage = "Please enter a valid amount greater than ₹0"
                        return@PrimaryButton
                    }
                    if (description.isBlank()) {
                        errorMessage = "Please enter a description"
                        return@PrimaryButton
                    }
                    onSubmit(
                        amt,
                        selectedCategoryId,
                        description,
                        notes.ifBlank { null },
                        expenseDate,
                        selectedPaymentMethod
                    )
                },
                isLoading = isLoading
            )

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
