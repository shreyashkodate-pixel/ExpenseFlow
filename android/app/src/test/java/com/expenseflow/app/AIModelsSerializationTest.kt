package com.expenseflow.app

import com.expenseflow.app.data.model.AIChatMessage
import com.expenseflow.app.data.model.AIChatRequest
import com.expenseflow.app.data.model.AIChatResponse
import com.expenseflow.app.data.model.AIRecommendationResponse
import com.expenseflow.app.data.model.Budget50_30_20
import com.expenseflow.app.data.model.PredictiveBudgetAlert
import com.expenseflow.app.data.model.SavingTip
import com.expenseflow.app.data.model.SpendingSpike
import com.expenseflow.app.data.model.SubscriptionAuditItem
import com.expenseflow.app.data.model.SubscriptionAuditResponse
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class AIModelsSerializationTest {

    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
        isLenient = true
        encodeDefaults = true
    }

    @Test
    fun testAIRecommendationSerialization() {
        val sampleResponse = AIRecommendationResponse(
            financialHealthScore = 82,
            healthStatus = "Good",
            headline = "Spending is well within budget targets with 18% savings pace.",
            spendingSpikes = listOf(
                SpendingSpike(
                    category = "Dining Out",
                    surgePercentage = 35.0,
                    insight = "Weekend dining increased by 35% compared to monthly average."
                )
            ),
            savingTips = listOf(
                SavingTip(
                    title = "Consolidate OTT Subscriptions",
                    description = "Cancel unused streaming platforms to save ₹1,200/mo.",
                    estimatedMonthlySavings = 1200.0,
                    category = "Entertainment"
                )
            ),
            predictiveBudgetAlerts = listOf(
                PredictiveBudgetAlert(
                    category = "Shopping",
                    currentSpend = 8500.0,
                    budgetLimit = 10000.0,
                    dailyBurnRate = 350.0,
                    projectedTotal = 11200.0,
                    projectedExhaustionDate = "September 24",
                    daysUntilExhaustion = 4,
                    safeDailyCeiling = 150.0,
                    pacingStatus = "caution",
                    alertMessage = "Shopping pace will exceed limit in 4 days at current ₹350/day spend."
                )
            ),
            subscriptionAudit = SubscriptionAuditResponse(
                detectedSubscriptions = listOf(
                    SubscriptionAuditItem(
                        merchantOrService = "Netflix",
                        amount = 649.0,
                        frequency = "Monthly",
                        category = "Entertainment"
                    )
                ),
                totalMonthlyRecurring = 649.0,
                subscriptionCount = 1,
                summaryTip = "1 recurring subscription found totaling ₹649/month."
            ),
            budget50_30_20 = Budget50_30_20(
                needsSpend = 15000.0,
                needsPct = 48.0,
                wantsSpend = 9000.0,
                wantsPct = 29.0,
                savingsSpend = 7000.0,
                savingsPct = 23.0,
                totalEvaluated = 31000.0,
                status = "balanced",
                rebalancingAdvice = "Your wealth allocation closely mirrors the healthy 50/30/20 benchmark."
            ),
            positiveHabits = listOf("Consistent savings allocation", "Utility bills paid on time"),
            providerUsed = "gemini",
            cached = false,
            generatedAt = "2026-09-08T19:00:00Z"
        )

        val serialized = json.encodeToString(sampleResponse)
        val deserialized = json.decodeFromString<AIRecommendationResponse>(serialized)

        assertEquals(82, deserialized.financialHealthScore)
        assertEquals("Good", deserialized.healthStatus)
        assertEquals(1, deserialized.spendingSpikes.size)
        assertEquals(35.0, deserialized.spendingSpikes[0].surgePercentage)
        assertEquals(1, deserialized.savingTips.size)
        assertEquals(1200.0, deserialized.savingTips[0].estimatedMonthlySavings)
        assertEquals(1, deserialized.predictiveBudgetAlerts.size)
        assertEquals("caution", deserialized.predictiveBudgetAlerts[0].pacingStatus)
        assertNotNull(deserialized.subscriptionAudit)
        assertEquals(1, deserialized.subscriptionAudit?.subscriptionCount)
        assertNotNull(deserialized.budget50_30_20)
        assertEquals(48.0, deserialized.budget50_30_20?.needsPct)
    }

    @Test
    fun testAIChatRequestAndResponseSerialization() {
        val request = AIChatRequest(
            message = "How much have I spent on groceries this month?",
            conversationHistory = listOf(
                AIChatMessage(role = "user", content = "Hello assistant"),
                AIChatMessage(role = "assistant", content = "Hi! How can I help you manage your expenses today?")
            )
        )

        val serializedReq = json.encodeToString(request)
        val deserializedReq = json.decodeFromString<AIChatRequest>(serializedReq)
        assertEquals(2, deserializedReq.conversationHistory.size)
        assertEquals("user", deserializedReq.conversationHistory[0].role)

        val responseJson = """
            {
                "reply": "You have spent ₹4,250 on groceries across 6 transactions.",
                "suggested_followups": [
                    "Compare with last month",
                    "What was the largest grocery purchase?"
                ],
                "data_points_referenced": [
                    "6 Groceries transactions",
                    "₹4,250 total spend"
                ],
                "provider_used": "gemini"
            }
        """.trimIndent()

        val parsedResponse = json.decodeFromString<AIChatResponse>(responseJson)
        assertTrue(parsedResponse.reply.contains("₹4,250"))
        assertEquals(2, parsedResponse.suggestedFollowups.size)
        assertEquals(2, parsedResponse.dataPointsReferenced.size)
        assertEquals("gemini", parsedResponse.providerUsed)
    }
}
