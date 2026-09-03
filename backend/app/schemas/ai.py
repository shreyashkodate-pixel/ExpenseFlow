from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SpendingSpike(BaseModel):
    category: str = Field(..., description="Category where the spending surge occurred")
    surge_percentage: Optional[float] = Field(None, description="Estimated percentage increase over baseline")
    insight: str = Field(..., description="Explanation of the unusual surge")


class SavingTip(BaseModel):
    title: str = Field(..., description="Brief actionable tip title")
    description: str = Field(..., description="Detailed practical recommendation to save money")
    estimated_monthly_savings: Optional[float] = Field(None, description="Estimated monthly savings in ₹")
    category: Optional[str] = Field(None, description="Associated spending category")


class BudgetWarning(BaseModel):
    category: str = Field(..., description="Category with pacing warning")
    status: str = Field(..., description="Status e.g. warning, critical, exceeded")
    message: str = Field(..., description="Pacing alert message")


class PredictiveBudgetAlert(BaseModel):
    category: str = Field(..., description="Budget category e.g. Shopping, Food, or Overall")
    current_spend: float = Field(..., description="Amount spent so far this month")
    budget_limit: float = Field(..., description="Total budget limit configured")
    daily_burn_rate: float = Field(..., description="Average daily spending in ₹")
    projected_total: float = Field(..., description="Projected month-end spending at current pace")
    projected_exhaustion_date: Optional[str] = Field(None, description="Forecasted day budget will run out e.g. 'September 18' or 'Exceeded'")
    days_until_exhaustion: Optional[int] = Field(None, description="Number of days remaining before exhaustion")
    safe_daily_ceiling: float = Field(..., description="Recommended daily limit to stay on track")
    pacing_status: str = Field(..., description="Pacing status: safe, caution, critical, or exceeded")
    alert_message: str = Field(..., description="Detailed proactive warning and advice")


class SubscriptionAuditItem(BaseModel):
    merchant_or_service: str = Field(..., description="Name of subscription/service e.g. Netflix, Spotify, Gym, Wi-Fi")
    amount: float = Field(..., description="Recurring charge amount in ₹")
    frequency: str = Field("Monthly", description="Frequency e.g. Monthly, Bi-weekly, Annual")
    category: str = Field(..., description="Spending category")
    last_charged_date: Optional[str] = Field(None, description="Date of most recent payment")
    optimization_tip: Optional[str] = Field(None, description="Cost-cutting recommendation")


class SubscriptionAuditResponse(BaseModel):
    detected_subscriptions: List[SubscriptionAuditItem] = Field(default_factory=list, description="Identified active recurring subscriptions")
    total_monthly_recurring: float = Field(0.0, description="Total monthly commitment overhead in ₹")
    subscription_count: int = Field(0, description="Total count of recurring subscriptions")
    summary_tip: str = Field(..., description="High-level audit assessment and savings opportunities")


class Budget50_30_20(BaseModel):
    needs_spend: float = Field(0.0, description="Total spent on Needs (Rent, Groceries, Utilities, Commute)")
    needs_pct: float = Field(0.0, description="Percentage of spending on Needs (Target: 50%)")
    wants_spend: float = Field(0.0, description="Total spent on Wants (Dining out, Shopping, Entertainment)")
    wants_pct: float = Field(0.0, description="Percentage of spending on Wants (Target: 30%)")
    savings_spend: float = Field(0.0, description="Total directed to Savings / Debt / Investments")
    savings_pct: float = Field(0.0, description="Percentage of spending on Savings (Target: 20%)")
    total_evaluated: float = Field(0.0, description="Total sum evaluated")
    status: str = Field("balanced", description="Status: balanced, wants_heavy, needs_heavy, or savings_low")
    rebalancing_advice: str = Field(..., description="Actionable advice to rebalance towards 50/30/20")


class AIChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    timestamp: Optional[datetime] = None


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User question or prompt")
    conversation_history: List[AIChatMessage] = Field(default_factory=list, description="Recent conversation turns for context")


class AIChatResponse(BaseModel):
    reply: str = Field(..., description="AI assistant response formatted in clean markdown")
    suggested_followups: List[str] = Field(default_factory=list, description="Quick follow-up questions for the user")
    data_points_referenced: List[str] = Field(default_factory=list, description="Specific database data points referenced")
    provider_used: str = Field("gemini", description="AI provider used: gemini, openai, claude")


class AIRecommendationResponse(BaseModel):
    financial_health_score: int = Field(..., ge=0, le=100, description="Overall financial health score (0-100)")
    health_status: str = Field(..., description="Status: Excellent, Good, Needs Attention, or Getting Started")
    headline: str = Field(..., description="One-sentence financial summary for the user")
    spending_spikes: List[SpendingSpike] = Field(default_factory=list, description="Detected unusual spending surges")
    saving_tips: List[SavingTip] = Field(default_factory=list, description="Actionable saving opportunities")
    budget_warnings: List[BudgetWarning] = Field(default_factory=list, description="Budget pacing alerts (legacy)")
    predictive_budget_alerts: List[PredictiveBudgetAlert] = Field(default_factory=list, description="Proactive overspending forecasts and daily pacing ceilings")
    subscription_audit: Optional[SubscriptionAuditResponse] = Field(None, description="Step 3: Subscription & recurring charges audit")
    budget_50_30_20: Optional[Budget50_30_20] = Field(None, description="Step 4: 50/30/20 budget framework analysis")
    positive_habits: List[str] = Field(default_factory=list, description="Positive financial behaviors observed")
    provider_used: str = Field("gemini", description="AI provider used: gemini, openai, claude")
    cached: bool = Field(False, description="Whether this response was served from cache")
    generated_at: datetime = Field(..., description="Timestamp of when insights were generated")
