package com.expenseflow.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SpendingSpike(
    val category: String,
    @SerialName("surge_percentage")
    val surgePercentage: Double? = null,
    val insight: String
)

@Serializable
data class SavingTip(
    val title: String,
    val description: String,
    @SerialName("estimated_monthly_savings")
    val estimatedMonthlySavings: Double? = null,
    val category: String? = null
)

@Serializable
data class BudgetWarning(
    val category: String,
    val status: String,
    val message: String
)

@Serializable
data class PredictiveBudgetAlert(
    val category: String,
    @SerialName("current_spend")
    val currentSpend: Double,
    @SerialName("budget_limit")
    val budgetLimit: Double,
    @SerialName("daily_burn_rate")
    val dailyBurnRate: Double,
    @SerialName("projected_total")
    val projectedTotal: Double,
    @SerialName("projected_exhaustion_date")
    val projectedExhaustionDate: String? = null,
    @SerialName("days_until_exhaustion")
    val daysUntilExhaustion: Int? = null,
    @SerialName("safe_daily_ceiling")
    val safeDailyCeiling: Double,
    @SerialName("pacing_status")
    val pacingStatus: String,
    @SerialName("alert_message")
    val alertMessage: String
)

@Serializable
data class SubscriptionAuditItem(
    @SerialName("merchant_or_service")
    val merchantOrService: String,
    val amount: Double,
    val frequency: String = "Monthly",
    val category: String,
    @SerialName("last_charged_date")
    val lastChargedDate: String? = null,
    @SerialName("optimization_tip")
    val optimizationTip: String? = null
)

@Serializable
data class SubscriptionAuditResponse(
    @SerialName("detected_subscriptions")
    val detectedSubscriptions: List<SubscriptionAuditItem> = emptyList(),
    @SerialName("total_monthly_recurring")
    val totalMonthlyRecurring: Double = 0.0,
    @SerialName("subscription_count")
    val subscriptionCount: Int = 0,
    @SerialName("summary_tip")
    val summaryTip: String
)

@Serializable
data class Budget50_30_20(
    @SerialName("needs_spend")
    val needsSpend: Double = 0.0,
    @SerialName("needs_pct")
    val needsPct: Double = 0.0,
    @SerialName("wants_spend")
    val wantsSpend: Double = 0.0,
    @SerialName("wants_pct")
    val wantsPct: Double = 0.0,
    @SerialName("savings_spend")
    val savingsSpend: Double = 0.0,
    @SerialName("savings_pct")
    val savingsPct: Double = 0.0,
    @SerialName("total_evaluated")
    val totalEvaluated: Double = 0.0,
    val status: String = "balanced",
    @SerialName("rebalancing_advice")
    val rebalancingAdvice: String
)

@Serializable
data class AIChatMessage(
    val role: String,
    val content: String,
    val timestamp: String? = null
)

@Serializable
data class AIChatRequest(
    val message: String,
    @SerialName("conversation_history")
    val conversationHistory: List<AIChatMessage> = emptyList()
)

@Serializable
data class AIChatResponse(
    val reply: String,
    @SerialName("suggested_followups")
    val suggestedFollowups: List<String> = emptyList(),
    @SerialName("data_points_referenced")
    val dataPointsReferenced: List<String> = emptyList(),
    @SerialName("provider_used")
    val providerUsed: String = "gemini"
)

@Serializable
data class AIRecommendationResponse(
    @SerialName("financial_health_score")
    val financialHealthScore: Int,
    @SerialName("health_status")
    val healthStatus: String,
    val headline: String,
    @SerialName("spending_spikes")
    val spendingSpikes: List<SpendingSpike> = emptyList(),
    @SerialName("saving_tips")
    val savingTips: List<SavingTip> = emptyList(),
    @SerialName("budget_warnings")
    val budgetWarnings: List<BudgetWarning> = emptyList(),
    @SerialName("predictive_budget_alerts")
    val predictiveBudgetAlerts: List<PredictiveBudgetAlert> = emptyList(),
    @SerialName("subscription_audit")
    val subscriptionAudit: SubscriptionAuditResponse? = null,
    @SerialName("budget_50_30_20")
    val budget50_30_20: Budget50_30_20? = null,
    @SerialName("positive_habits")
    val positiveHabits: List<String> = emptyList(),
    @SerialName("provider_used")
    val providerUsed: String = "gemini",
    val cached: Boolean = false,
    @SerialName("generated_at")
    val generatedAt: String
)
