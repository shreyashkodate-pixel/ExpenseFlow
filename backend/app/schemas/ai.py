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


class AIRecommendationResponse(BaseModel):
    financial_health_score: int = Field(..., ge=0, le=100, description="Overall financial health score (0-100)")
    health_status: str = Field(..., description="Status: Excellent, Good, Needs Attention, or Getting Started")
    headline: str = Field(..., description="One-sentence financial summary for the user")
    spending_spikes: List[SpendingSpike] = Field(default_factory=list, description="Detected unusual spending surges")
    saving_tips: List[SavingTip] = Field(default_factory=list, description="Actionable saving opportunities")
    budget_warnings: List[BudgetWarning] = Field(default_factory=list, description="Budget pacing alerts (legacy)")
    predictive_budget_alerts: List[PredictiveBudgetAlert] = Field(default_factory=list, description="Proactive overspending forecasts and daily pacing ceilings")
    positive_habits: List[str] = Field(default_factory=list, description="Positive financial behaviors observed")
    provider_used: str = Field("gemini", description="AI provider used: gemini, openai, claude")
    cached: bool = Field(False, description="Whether this response was served from cache")
    generated_at: datetime = Field(..., description="Timestamp of when insights were generated")
