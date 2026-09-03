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
    PredictiveBudgetAlert,
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

    # 3. Calculate predictive budget pacing for all active budgets
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == today.month,
        Budget.year == today.year,
    ).all()

    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)
    total_days_in_month = (next_month_start - month_start).days
    days_elapsed = max(1, today.day)
    days_remaining = max(1, total_days_in_month - today.day)

    predictive_pacing_data = []
    budget_info = None

    for b in budgets:
        b_amt = float(b.amount)
        if b_amt <= 0:
            continue

        if b.category_id is None:
            cat_label = "Overall"
            spent = current_month_total
            budget_info = {
                "monthly_budget": b_amt,
                "spent": spent,
                "remaining": max(0.0, b_amt - spent),
                "utilization_pct": round((spent / b_amt) * 100, 1),
                "days_remaining_in_month": days_remaining,
            }
        else:
            cat_label = cat_map.get(b.category_id, "Category")
            spent = month_cat_totals.get(cat_label, 0.0)

        daily_burn = round(spent / days_elapsed, 2)
        projected_total = round(daily_burn * total_days_in_month, 2)
        rem_budget = max(0.0, b_amt - spent)
        safe_ceiling = round(rem_budget / days_remaining, 2)

        if spent >= b_amt:
            pacing_status = "exceeded"
            exhaustion_date = "Exceeded"
            days_left = 0
            alert_msg = f"You have already spent ₹{spent:,.0f} exceeding your {cat_label} budget of ₹{b_amt:,.0f} by ₹{spent - b_amt:,.0f}."
        elif daily_burn > 0:
            days_left = int(rem_budget / daily_burn)
            if days_left < days_remaining:
                exhaustion_day = min(total_days_in_month, today.day + days_left)
                try:
                    exhaustion_date = date(today.year, today.month, exhaustion_day).strftime("%B %d")
                except ValueError:
                    exhaustion_date = f"Day {exhaustion_day}"
                pacing_status = "critical" if days_left <= 7 else "caution"
                alert_msg = f"At your current pace of ₹{daily_burn:,.0f}/day on {cat_label}, you will exceed your ₹{b_amt:,.0f} budget by {exhaustion_date}. Limit spending to ₹{safe_ceiling:,.0f}/day to stay on track."
            else:
                pacing_status = "safe"
                exhaustion_date = None
                days_left = None
                alert_msg = f"Your {cat_label} spending is on track at ₹{daily_burn:,.0f}/day. Your safe daily spending ceiling is ₹{safe_ceiling:,.0f}/day."
        else:
            pacing_status = "safe"
            exhaustion_date = None
            days_left = None
            alert_msg = f"No spending yet on {cat_label}. Safe daily ceiling is ₹{safe_ceiling:,.0f}/day."

        predictive_pacing_data.append({
            "category": cat_label,
            "current_spend": round(spent, 2),
            "budget_limit": round(b_amt, 2),
            "daily_burn_rate": daily_burn,
            "projected_total": projected_total,
            "projected_exhaustion_date": exhaustion_date,
            "days_until_exhaustion": days_left,
            "safe_daily_ceiling": safe_ceiling,
            "pacing_status": pacing_status,
            "alert_message": alert_msg,
        })

    return {
        "total_expenses_count": len(month_expenses),
        "current_month_total": round(current_month_total, 2),
        "category_breakdown": {k: round(v, 2) for k, v in month_cat_totals.items()},
        "detected_surges": detected_surges,
        "top_transactions": top_transactions,
        "budget_info": budget_info,
        "predictive_pacing_data": predictive_pacing_data,
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
        '  "predictive_budget_alerts": [\n'
        '    {"category": "<Category or Overall>", "alert_message": "<Early warning e.g. At your current pace of ₹650/day on Shopping, you will exceed your ₹10,000 budget by the 18th. Limit spending to ₹280/day to stay on track.>"}\n'
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
- Active Budgets & Pacing Projections: {summary.get('predictive_pacing_data', [])}

Analyze these numbers. Pinpoint 1-2 unusual category spikes (if any), offer 2-3 specific, realistic saving recommendations with estimated ₹ monthly savings, provide proactive early-warning predictive budget overspending alerts with daily spending limits, and provide an overall financial health score.
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

        # Build ground-truth predictive budget alerts
        ai_alert_map = {
            a.get("category"): a.get("alert_message")
            for a in raw_json.get("predictive_budget_alerts", [])
            if isinstance(a, dict) and a.get("category")
        }

        predictive_alerts = []
        for p in summary.get("predictive_pacing_data", []):
            cat = p.get("category", "Overall")
            msg = ai_alert_map.get(cat) or p.get("alert_message", "")
            predictive_alerts.append(
                PredictiveBudgetAlert(
                    category=cat,
                    current_spend=p.get("current_spend", 0.0),
                    budget_limit=p.get("budget_limit", 0.0),
                    daily_burn_rate=p.get("daily_burn_rate", 0.0),
                    projected_total=p.get("projected_total", 0.0),
                    projected_exhaustion_date=p.get("projected_exhaustion_date"),
                    days_until_exhaustion=p.get("days_until_exhaustion"),
                    safe_daily_ceiling=p.get("safe_daily_ceiling", 0.0),
                    pacing_status=p.get("pacing_status", "safe"),
                    alert_message=msg,
                )
            )

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
            predictive_budget_alerts=predictive_alerts,
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

    predictive_alerts = [
        PredictiveBudgetAlert(
            category=p.get("category", "Overall"),
            current_spend=p.get("current_spend", 0.0),
            budget_limit=p.get("budget_limit", 0.0),
            daily_burn_rate=p.get("daily_burn_rate", 0.0),
            projected_total=p.get("projected_total", 0.0),
            projected_exhaustion_date=p.get("projected_exhaustion_date"),
            days_until_exhaustion=p.get("days_until_exhaustion"),
            safe_daily_ceiling=p.get("safe_daily_ceiling", 0.0),
            pacing_status=p.get("pacing_status", "safe"),
            alert_message=p.get("alert_message", ""),
        )
        for p in summary.get("predictive_pacing_data", [])
    ]

    return AIRecommendationResponse(
        financial_health_score=score,
        health_status=status,
        headline=f"Your highest expenditure category this month is {top_cat} totaling ₹{top_spend:,.0f}.",
        spending_spikes=[],
        saving_tips=tips,
        budget_warnings=warnings,
        predictive_budget_alerts=predictive_alerts,
        positive_habits=["Consistent expense tracking will reveal more optimization insights over time."],
        provider_used="rule-engine",
        cached=False,
        generated_at=now,
    )
