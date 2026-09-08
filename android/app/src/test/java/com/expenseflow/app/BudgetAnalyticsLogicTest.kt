package com.expenseflow.app

import com.expenseflow.app.data.model.BudgetStatusItem
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class BudgetAnalyticsLogicTest {

    @Test
    fun testOverallBudgetPacingPercentages() {
        val pacing = BudgetStatusItem(
            categoryName = "Overall",
            budgetAmount = 50000.0,
            spentAmount = 32500.0,
            remainingAmount = 17500.0,
            percentageUsed = 65.0,
            statusLevel = "ok"
        )

        assertEquals(65.0, pacing.percentageUsed, 0.001)
        assertEquals("ok", pacing.statusLevel)
        assertEquals(17500.0, pacing.remainingAmount, 0.001)
        assertTrue(pacing.percentageUsed < 80.0)
    }

    @Test
    fun testCategoryExceededPacing() {
        val categoryPacing = BudgetStatusItem(
            categoryName = "Food & Dining",
            budgetAmount = 12000.0,
            spentAmount = 13500.0,
            remainingAmount = -1500.0,
            percentageUsed = 112.5,
            statusLevel = "exceeded"
        )

        assertEquals("exceeded", categoryPacing.statusLevel)
        assertTrue(categoryPacing.percentageUsed > 100.0)
        assertTrue(categoryPacing.remainingAmount < 0.0)
    }
}
