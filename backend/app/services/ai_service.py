import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.config import settings
from ..models.expense import Expense
from ..models.category import Category
from ..models.budget import Budget
from ..schemas.ai import (
    AIRecommendationResponse,
    SpendingSpike,
    SavingTip,
    BudgetWarning,
)
from .ai.factory import get_ai_provider

logger = logging.getLogger(__name__)

# In-memory sliding cache: user_id -> (timestamp, AIRecommendationResponse)
_recommendations_cache: Dict[int, tuple[datetime, AIRecommendationResponse]] = {}


def clear_ai_cache() -> None:
    """Clear in-memory recommendation cache (used in tests and maintenance)."""
    _recommendations_cache.clear()



def _get_user_spending_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Safely aggregate the user's spending data into an anonymized financial context.
    Strictly isolated to user_id. No user names, emails, or PII are extracted.
    """
    today = date.today()
    month_start = date(today.year, today.month, 1)
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)

    # 1. Fetch categories mapping
    categories = db.query(Category).filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None))
    ).all()
    cat_map = {c.id: c.name for c in categories}

    # 2. Fetch all expenses from the past 30 days
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= thirty_days_ago
    ).order_by(Expense.date.desc()).all()

    if not expenses:
        return {"total_expenses_count": 0}

    month_expenses = [e for e in expenses if e.date >= month_start]
    current_month_total = float(sum(e.amount for e in month_expenses))

    # Category totals for current month
    month_cat_totals: Dict[str, float] = defaultdict(float)
    for e in month_expenses:
        cat_name = cat_map.get(e.category_id, "Other")
        month_cat_totals[cat_name] += float(e.amount)

    # Spike detection data: 7-day spend vs baseline (previous 23 days)
    last_7_days_cat: Dict[str, float] = defaultdict(float)
    prev_23_days_cat: Dict[str, float] = defaultdict(float)

    for e in expenses:
        cat_name = cat_map.get(e.category_id, "Other")
        if e.date >= seven_days_ago:
            last_7_days_cat[cat_name] += float(e.amount)
        else:
            prev_23_days_cat[cat_name] += float(e.amount)

    # Identify potential surge candidates (where 7-day rate exceeds normalized weekly baseline)
    detected_surges = []
    for cat, recent_spend in last_7_days_cat.items():
        baseline_weekly = (prev_23_days_cat.get(cat, 0) / 23.0) * 7.0
        if baseline_weekly > 0 and recent_spend > baseline_weekly * 1.25 and recent_spend >= 300:
            pct_increase = round(((recent_spend - baseline_weekly) / baseline_weekly) * 100, 1)
            detected_surges.append({
                "category": cat,
                "recent_7d_spend": round(recent_spend, 2),
                "baseline_weekly": round(baseline_weekly, 2),
                "surge_percentage": pct_increase,
            })

    # Highest individual transaction
    sorted_by_amount = sorted(month_expenses, key=lambda x: x.amount, reverse=True)
    top_transactions = [
        {"description": e.description or cat_map.get(e.category_id, "Expense"), "amount": float(e.amount), "category": cat_map.get(e.category_id, "Other")}
        for e in sorted_by_amount[:3]
    ]

    # Active budget
    active_budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == today.month,
        Budget.year == today.year,
        Budget.category_id.is_(None)
    ).first()

    budget_info = None
    if active_budget and active_budget.amount > 0:
        budget_amt = float(active_budget.amount)
        utilization_pct = round((current_month_total / budget_amt) * 100, 1)
        budget_info = {
            "monthly_budget": budget_amt,
            "spent": current_month_total,
            "remaining": max(0.0, budget_amt - current_month_total),
            "utilization_pct": utilization_pct,
            "days_remaining_in_month": (date(today.year, today.month + 1 if today.month < 12 else 1, 1) - today).days,
        }

    return {
        "total_expenses_count": len(month_expenses),
        "current_month_total": round(current_month_total, 2),
        "category_breakdown": {k: round(v, 2) for k, v in month_cat_totals.items()},
        "detected_surges": detected_surges,
        "top_transactions": top_transactions,
        "budget_info": budget_info,
    }


def get_ai_recommendations(db: Session, user_id: int, force_refresh: bool = False) -> AIRecommendationResponse:
    """
    Generate or retrieve cached AI financial recommendations for the authenticated user.
    Uses the active environment-configured provider (Gemini, OpenAI, Claude).
    """
    now = datetime.now(timezone.utc)

    # 1. Check in-memory cache if not force refreshing
    if not force_refresh and user_id in _recommendations_cache:
        cached_time, cached_response = _recommendations_cache[user_id]
        cache_validity = timedelta(hours=max(1, settings.AI_CACHE_HOURS))
        if now - cached_time < cache_validity:
            # Return cached response with cached=True
            return cached_response.model_copy(update={"cached": True})

    # 2. Gather user's anonymized financial context
    summary = _get_user_spending_summary(db, user_id)

    # If new account with insufficient data
    if summary.get("total_expenses_count", 0) < 2:
        empty_res = AIRecommendationResponse(
            financial_health_score=100,
            health_status="Getting Started",
            headline="Start logging your daily expenses to unlock personalized AI saving insights.",
            spending_spikes=[],
            saving_tips=[
                SavingTip(
                    title="Log Your First Few Expenses",
                    description="Record regular expenses like groceries, transport, or food to help ExpenseFlow AI uncover spending patterns and saving opportunities.",
                    estimated_monthly_savings=None,
                    category="General"
                )
            ],
            budget_warnings=[],
            positive_habits=["Welcome to ExpenseFlow! Tracking is the first step to financial freedom."],
            provider_used=settings.AI_PROVIDER,
            cached=False,
            generated_at=now,
        )
        _recommendations_cache[user_id] = (now, empty_res)
        return empty_res

    # 3. Formulate Prompt for the AI Provider
    system_instruction = (
        "You are ExpenseFlow AI, an intelligent, practical personal finance advisor. "
        "Analyze the user's spending data and provide realistic, motivating, and actionable insights. "
        "Strictly adhere to the user's local currency format (₹ INR). "
        "You MUST respond ONLY with valid JSON matching this exact structure:\n"
        "{\n"
        '  "financial_health_score": <int 0-100>,\n'
        '  "health_status": <"Excellent" | "Good" | "Needs Attention">,\n'
        '  "headline": <concise 1-sentence financial snapshot>,\n'
        '  "spending_spikes": [\n'
        '    {"category": "<Category>", "surge_percentage": <float or null>, "insight": "<e.g. You spent 42% more on Dining Out this week compared to your 30-day average.>"}\n'
        "  ],\n"
        '  "saving_tips": [\n'
        '    {"title": "<Tip Title>", "description": "<Actionable advice>", "estimated_monthly_savings": <numeric amount in INR e.g. 2500>, "category": "<Category>"}\n'
        "  ],\n"
        '  "budget_warnings": [\n'
        '    {"category": "<Category or Overall>", "status": "<warning | critical>", "message": "<Pacing alert e.g. At ₹650/day on Shopping, you will exceed your budget by the 18th.>"}\n'
        "  ],\n"
        '  "positive_habits": [\n'
        '    "<Encouraging highlight where the user remained disciplined>"\n'
        "  ]\n"
        "}"
    )

    prompt = f"""User Financial Metrics for Current Month:
- Total Month Spend: ₹{summary.get('current_month_total', 0)}
- Category Spending Breakdown: {summary.get('category_breakdown', {})}
- Detected 7-Day Spending Surges: {summary.get('detected_surges', [])}
- Top Individual Transactions: {summary.get('top_transactions', [])}
- Budget Context: {summary.get('budget_info', 'No overall budget configured')}

Analyze these numbers. Pinpoint 1-2 unusual category spikes (if any), offer 2-3 specific, realistic saving recommendations with estimated ₹ monthly savings, highlight any budget pacing risks, and provide an overall financial health score.
"""

    provider = get_ai_provider()
    try:
        raw_json = provider.generate_structured_json(prompt=prompt, system_instruction=system_instruction)
    except Exception as e:
        logger.error(f"Failed to generate recommendations via AI provider: {e}")
        # Fallback to local rule-based recommendations if external LLM fails
        return _generate_fallback_recommendations(summary, now)

    # 4. Parse into schema
    try:
        spikes = [
            SpendingSpike(
                category=s.get("category", "General"),
                surge_percentage=s.get("surge_percentage"),
                insight=s.get("insight", "")
            )
            for s in raw_json.get("spending_spikes", [])
        ]

        tips = [
            SavingTip(
                title=t.get("title", "Smart Tip"),
                description=t.get("description", ""),
                estimated_monthly_savings=t.get("estimated_monthly_savings"),
                category=t.get("category")
            )
            for t in raw_json.get("saving_tips", [])
        ]

        warnings = [
            BudgetWarning(
                category=w.get("category", "Overall"),
                status=w.get("status", "warning"),
                message=w.get("message", "")
            )
            for w in raw_json.get("budget_warnings", [])
        ]

        positive_habits = raw_json.get("positive_habits", [])
        if not isinstance(positive_habits, list):
            positive_habits = [str(positive_habits)]

        score = max(0, min(100, int(raw_json.get("financial_health_score", 75))))
        status = raw_json.get("health_status", "Good")
        if score >= 80:
            status = "Excellent"
        elif score < 60:
            status = "Needs Attention"

        response_obj = AIRecommendationResponse(
            financial_health_score=score,
            health_status=status,
            headline=raw_json.get("headline", "Here are your personalized spending insights."),
            spending_spikes=spikes,
            saving_tips=tips,
            budget_warnings=warnings,
            positive_habits=positive_habits,
            provider_used=settings.AI_PROVIDER,
            cached=False,
            generated_at=now,
        )

        # Cache in memory
        _recommendations_cache[user_id] = (now, response_obj)
        return response_obj

    except Exception as parse_ex:
        logger.error(f"Error parsing AI response into schema: {parse_ex}")
        return _generate_fallback_recommendations(summary, now)


def _generate_fallback_recommendations(summary: Dict[str, Any], now: datetime) -> AIRecommendationResponse:
    """Deterministic fallback if AI provider is temporarily unavailable or misconfigured."""
    cat_breakdown = summary.get("category_breakdown", {})
    total = summary.get("current_month_total", 0)

    top_cat = max(cat_breakdown.items(), key=lambda x: x[1])[0] if cat_breakdown else "General"
    top_spend = cat_breakdown.get(top_cat, 0)

    tips = []
    if top_spend > 0:
        est_save = round(top_spend * 0.15, -1)
        tips.append(
            SavingTip(
                title=f"Optimize {top_cat} Spending",
                description=f"Your highest spending category this month is {top_cat} (₹{top_spend}). Trimming minor discretionary purchases in this category could easily save around ₹{est_save}/month.",
                estimated_monthly_savings=est_save,
                category=top_cat,
            )
        )

    budget_info = summary.get("budget_info")
    warnings = []
    if budget_info:
        utilization = float(budget_info.get("utilization_pct", 0))
        spent = float(budget_info.get("spent", 0))
        budget_amt = float(budget_info.get("monthly_budget", 0))
        if utilization > 100:
            score = max(25, int(100 - (utilization - 100) * 0.75))
            status = "Needs Attention"
            warnings.append(
                BudgetWarning(
                    category="Overall",
                    status="exceeded",
                    message=f"You have spent ₹{spent:,.0f} exceeding your monthly budget of ₹{budget_amt:,.0f} ({utilization:.0f}% utilized)."
                )
            )
        elif utilization >= 80:
            score = max(55, int(100 - (utilization - 80) * 1.5))
            status = "Needs Attention" if score < 60 else "Good"
            warnings.append(
                BudgetWarning(
                    category="Overall",
                    status="warning",
                    message=f"You have used {utilization:.0f}% of your monthly budget (₹{spent:,.0f} of ₹{budget_amt:,.0f})."
                )
            )
        else:
            score = 85
            status = "Excellent"
    else:
        score = 75
        status = "Good"

    return AIRecommendationResponse(
        financial_health_score=score,
        health_status=status,
        headline=f"Your highest expenditure category this month is {top_cat} totaling ₹{top_spend:,.0f}.",
        spending_spikes=[],
        saving_tips=tips,
        budget_warnings=warnings,
        positive_habits=["Consistent expense tracking will reveal more optimization insights over time."],
        provider_used="rule-engine",
        cached=False,
        generated_at=now,
    )
