import logging
import re
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional, List
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
    SubscriptionAuditItem,
    SubscriptionAuditResponse,
    Budget50_30_20,
    AIChatRequest,
    AIChatResponse,
    AIChatMessage,
)
from .ai.factory import get_ai_provider

logger = logging.getLogger(__name__)

# In-memory sliding cache: user_id -> (timestamp, AIRecommendationResponse)
_recommendations_cache: Dict[int, tuple[datetime, AIRecommendationResponse]] = {}


def clear_ai_cache() -> None:
    """Clear in-memory recommendation cache (used in tests and maintenance)."""
    _recommendations_cache.clear()


# Common recurring subscription/bill keyword patterns
RECURRING_KEYWORD_PATTERNS = [
    (r"\b(netflix)\b", "Netflix", "Entertainment", "Review unviewed months or evaluate family plan sharing."),
    (r"\b(spotify)\b", "Spotify", "Entertainment", "Consider an Annual or Duo plan to save up to 20%."),
    (r"\b(prime|amazon prime)\b", "Amazon Prime", "Shopping", "Ensure you use Prime Video & Music to maximize subscription value."),
    (r"\b(youtube|youtube premium)\b", "YouTube Premium", "Entertainment", "Check family tier if multiple household members use it."),
    (r"\b(hotstar|disney)\b", "Disney+ Hotstar", "Entertainment", "Audit viewing frequency; pause between sports/shows seasons."),
    (r"\b(gym|fitness|cult\.?fit)\b", "Gym & Fitness Membership", "Health & Fitness", "Ask about annual prepaid discounts or off-peak pricing."),
    (r"\b(wifi|broadband|airtel|jio|act fibernet)\b", "Wi-Fi & Broadband", "Bills & Utilities", "Review data plan tiers if current speed exceeds your needs."),
    (r"\b(rent|house rent)\b", "House Rent", "Housing", "Fixed monthly obligation; ensure timely payment for credit score."),
    (r"\b(maintenance|society maintenance)\b", "Society Maintenance", "Housing", "Fixed monthly living utility."),
    (r"\b(sip|mutual fund|zerodha|groww)\b", "Systematic Investment Plan (SIP)", "Investments", "Great discipline! Continue automating your wealth building."),
    (r"\b(emi|loan)\b", "Loan EMI", "Debt / Loans", "Prioritize prepaying high-interest loans early when cash is available."),
    (r"\b(insurance|lic|term insurance)\b", "Insurance Premium", "Financial Services", "Essential financial safety net."),
    (r"\b(icloud|google one|dropbox|cloud storage)\b", "Cloud Storage", "Technology", "Clean up large photos/videos to downsize storage tier."),
    (r"\b(chatgpt|openai|cursor|github|copilot)\b", "AI / Dev Tool Subscription", "Technology", "Review active usage across team/personal plans."),
]


def _detect_subscriptions(db: Session, user_id: int, cat_map: Dict[int, str]) -> SubscriptionAuditResponse:
    """
    Step 3: Automatically detects recurring subscriptions and fixed commitments
    from past 90 days of transactions.
    """
    ninety_days_ago = date.today() - timedelta(days=90)
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= ninety_days_ago
    ).order_by(Expense.date.desc()).all()

    detected_map: Dict[str, SubscriptionAuditItem] = {}

    for exp in expenses:
        desc = (exp.description or "").lower()
        amt = float(exp.amount)
        cat_name = cat_map.get(exp.category_id, "Utilities")
        exp_date_str = exp.date.strftime("%B %d, %Y")

        matched = False
        for pattern, clean_name, default_cat, tip in RECURRING_KEYWORD_PATTERNS:
            if re.search(pattern, desc, re.IGNORECASE):
                if clean_name not in detected_map:
                    detected_map[clean_name] = SubscriptionAuditItem(
                        merchant_or_service=clean_name,
                        amount=amt,
                        frequency="Monthly",
                        category=cat_name or default_cat,
                        last_charged_date=exp_date_str,
                        optimization_tip=tip,
                    )
                matched = True
                break

        # Fallback: repeating exact descriptions with >= 2 occurrences in 90 days
        if not matched and exp.description and len(exp.description.strip()) >= 3:
            key = exp.description.strip().title()
            if key not in detected_map:
                # Count matching occurrences in the 90 days
                matching_count = sum(
                    1 for other in expenses
                    if (other.description or "").strip().lower() == desc
                    and abs(float(other.amount) - amt) < 1.0
                )
                if matching_count >= 2:
                    detected_map[key] = SubscriptionAuditItem(
                        merchant_or_service=key,
                        amount=amt,
                        frequency="Monthly",
                        category=cat_name,
                        last_charged_date=exp_date_str,
                        optimization_tip=f"Recurring payment identified ({matching_count} times in 90 days). Review if still actively utilized.",
                    )

    subscriptions = list(detected_map.values())
    total_recurring = round(sum(s.amount for s in subscriptions), 2)
    count = len(subscriptions)

    if count > 0:
        summary_tip = f"You have {count} identified recurring commitments totaling ₹{total_recurring:,.0f}/month. Review optional subscriptions periodically to eliminate 'zombie' charges."
    else:
        summary_tip = "No recurring monthly subscriptions detected yet. Regular recurring bills (streaming, gym, Wi-Fi) will be audited here automatically."

    return SubscriptionAuditResponse(
        detected_subscriptions=subscriptions,
        total_monthly_recurring=total_recurring,
        subscription_count=count,
        summary_tip=summary_tip,
    )


def _calculate_50_30_20(month_expenses: List[Expense], cat_map: Dict[int, str], total_spent: float) -> Budget50_30_20:
    """
    Step 4: Maps expenses into the classic 50/30/20 Personal Wealth Framework:
    - 50% Needs: Essential non-negotiables (Rent, Groceries, Utilities, Commute, Healthcare)
    - 30% Wants: Lifestyle and comfort (Dining out, Shopping, Entertainment, Vacations)
    - 20% Savings: Wealth accumulation (Investments, SIP, Mutual Funds, Emergency Fund)
    """
    if total_spent <= 0:
        return Budget50_30_20(
            needs_spend=0.0,
            needs_pct=0.0,
            wants_spend=0.0,
            wants_pct=0.0,
            savings_spend=0.0,
            savings_pct=0.0,
            total_evaluated=0.0,
            status="balanced",
            rebalancing_advice="Start logging your expenses to view your 50/30/20 financial distribution.",
        )

    needs_keywords = {"grocer", "rent", "housing", "utilit", "bill", "electric", "water", "gas", "wifi", "internet", "commute", "transport", "fuel", "petrol", "medic", "health", "insurance", "tuition", "educat", "school"}
    savings_keywords = {"saving", "invest", "sip", "deposit", "emergency", "stock", "mutual fund", "fund", "prepay", "loan", "debt", "emi"}

    needs_spend = 0.0
    savings_spend = 0.0
    wants_spend = 0.0

    for exp in month_expenses:
        amt = float(exp.amount)
        cat_name = cat_map.get(exp.category_id, "").lower()
        desc = (exp.description or "").lower()
        combined = f"{cat_name} {desc}"

        if any(kw in combined for kw in savings_keywords):
            savings_spend += amt
        elif any(kw in combined for kw in needs_keywords):
            needs_spend += amt
        else:
            # Everything else defaults to Wants (Dining, Shopping, Entertainment, etc.)
            wants_spend += amt

    needs_pct = round((needs_spend / total_spent) * 100, 1)
    wants_pct = round((wants_spend / total_spent) * 100, 1)
    savings_pct = round((savings_spend / total_spent) * 100, 1)

    if wants_pct > 35:
        status = "wants_heavy"
        excess = round(wants_spend - (total_spent * 0.30), -1)
        rebalancing_advice = (
            f"Your lifestyle spending ('Wants') is currently at {wants_pct:.0f}% of total spend, exceeding the 30% target. "
            f"Trimming approximately ₹{excess:,.0f} from discretionary shopping and dining out will bring your budget into balance and boost your savings."
        )
    elif savings_pct < 15:
        status = "savings_low"
        deficit = round(max(0.0, (total_spent * 0.20) - savings_spend), -1)
        rebalancing_advice = (
            f"Your savings rate is currently {savings_pct:.0f}%, below the ideal 20% target. "
            f"Aim to redirect an additional ₹{deficit:,.0f} from discretionary categories into a high-yield emergency fund or SIPs this month."
        )
    elif needs_pct > 60:
        status = "needs_heavy"
        rebalancing_advice = (
            f"Essential living expenses ('Needs') represent {needs_pct:.0f}% of your spending (target: 50%). "
            "Consider reviewing utility plans or fixed housing overhead to increase flexibility."
        )
    else:
        status = "balanced"
        rebalancing_advice = (
            f"Healthy balance! Your monthly spending aligns well with the 50/30/20 guideline "
            f"({needs_pct:.0f}% Needs, {wants_pct:.0f}% Wants, {savings_pct:.0f}% Savings)."
        )

    return Budget50_30_20(
        needs_spend=round(needs_spend, 2),
        needs_pct=needs_pct,
        wants_spend=round(wants_spend, 2),
        wants_pct=wants_pct,
        savings_spend=round(savings_spend, 2),
        savings_pct=savings_pct,
        total_evaluated=round(total_spent, 2),
        status=status,
        rebalancing_advice=rebalancing_advice,
    )


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

    # 2. Fetch current month expenses
    month_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= month_start
    ).all()

    current_month_total = 0.0
    month_cat_totals = defaultdict(float)
    for e in month_expenses:
        amt = float(e.amount)
        current_month_total += amt
        cat_name = cat_map.get(e.category_id, "Other")
        month_cat_totals[cat_name] += amt

    # 3. Detect spending surges (7-day vs previous 23-day daily average)
    past_30d_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= thirty_days_ago
    ).all()

    cat_7d_spend = defaultdict(float)
    cat_prev_spend = defaultdict(float)

    for e in past_30d_expenses:
        amt = float(e.amount)
        cat_name = cat_map.get(e.category_id, "Other")
        if e.date >= seven_days_ago:
            cat_7d_spend[cat_name] += amt
        else:
            cat_prev_spend[cat_name] += amt

    detected_surges = []
    for cat_name, recent_spend in cat_7d_spend.items():
        prev_spend = cat_prev_spend.get(cat_name, 0.0)
        baseline_weekly = (prev_spend / 23.0) * 7.0

        if baseline_weekly > 100 and recent_spend > baseline_weekly * 1.3:
            pct_increase = round(((recent_spend - baseline_weekly) / baseline_weekly) * 100, 1)
            detected_surges.append({
                "category": cat_name,
                "recent_7d_spend": round(recent_spend, 2),
                "baseline_weekly": round(baseline_weekly, 2),
                "surge_percentage": pct_increase,
            })

    # Highest individual transactions
    sorted_by_amount = sorted(month_expenses, key=lambda x: x.amount, reverse=True)
    top_transactions = [
        {"description": e.description or cat_map.get(e.category_id, "Expense"), "amount": float(e.amount), "category": cat_map.get(e.category_id, "Other")}
        for e in sorted_by_amount[:5]
    ]

    # 4. Calculate predictive budget pacing for all active budgets (Step 2)
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

    # 5. Audit Subscriptions (Step 3)
    subscription_audit = _detect_subscriptions(db, user_id, cat_map)

    # 6. Calculate 50/30/20 Distribution (Step 4)
    budget_50_30_20 = _calculate_50_30_20(month_expenses, cat_map, current_month_total)

    return {
        "total_expenses_count": len(month_expenses),
        "current_month_total": round(current_month_total, 2),
        "category_breakdown": {k: round(v, 2) for k, v in month_cat_totals.items()},
        "detected_surges": detected_surges,
        "top_transactions": top_transactions,
        "budget_info": budget_info,
        "predictive_pacing_data": predictive_pacing_data,
        "subscription_audit": subscription_audit,
        "budget_50_30_20": budget_50_30_20,
    }


def get_ai_recommendations(db: Session, user_id: int, force_refresh: bool = False) -> AIRecommendationResponse:
    """
    Generate or retrieve cached AI financial recommendations for the authenticated user.
    Uses the active environment-configured provider (Gemini, OpenAI, Claude).
    """
    now = datetime.now(timezone.utc)

    # 1. Check in-memory cache if not force refreshing
    if not force_refresh and user_id in _recommendations_cache:
        cached_time, cached_data = _recommendations_cache[user_id]
        cache_duration = timedelta(hours=settings.AI_CACHE_HOURS)
        if now - cached_time < cache_duration:
            return cached_data.model_copy(update={"cached": True})

    # 2. Safely aggregate user financial metrics
    summary = _get_user_spending_summary(db, user_id)

    # If the user has logged very few expenses, return an encouraging onboarding state
    if summary["total_expenses_count"] < 2:
        empty_res = AIRecommendationResponse(
            financial_health_score=100,
            health_status="Getting Started",
            headline="Welcome to ExpenseFlow! Start logging your daily expenses to unlock AI-driven spending intelligence.",
            spending_spikes=[],
            saving_tips=[
                SavingTip(
                    title="Log Your First Few Expenses",
                    description="Record your daily purchases across Food, Shopping, and Bills. The AI will immediately start analyzing patterns and finding savings opportunities.",
                    estimated_monthly_savings=1500.0,
                    category="General"
                )
            ],
            budget_warnings=[],
            predictive_budget_alerts=[],
            subscription_audit=summary.get("subscription_audit"),
            budget_50_30_20=summary.get("budget_50_30_20"),
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
            subscription_audit=summary.get("subscription_audit"),
            budget_50_30_20=summary.get("budget_50_30_20"),
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
                description=f"Your highest spending category this month is {top_cat} (₹{top_spend:,.0f}). Trimming minor discretionary purchases in this category could easily save around ₹{est_save:,.0f}/month.",
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
        subscription_audit=summary.get("subscription_audit"),
        budget_50_30_20=summary.get("budget_50_30_20"),
        positive_habits=["Consistent expense tracking will reveal more optimization insights over time."],
        provider_used="rule-engine",
        cached=False,
        generated_at=now,
    )


# ---------------------------------------------------------------------------
# Step 5: Structured RAG Conversational Financial Assistant
# ---------------------------------------------------------------------------

def chat_with_ai(db: Session, user_id: int, request: AIChatRequest) -> AIChatResponse:
    """
    Step 5: Structured Financial RAG Assistant.
    Retrieves live relational ground truth from the database for user_id,
    injects exact tabular metrics, and streams an articulate, accurate answer.
    """
    summary = _get_user_spending_summary(db, user_id)
    today = date.today()

    # Retrieve last month's spending for comparative questions
    first_of_month = date(today.year, today.month, 1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = date(last_month_end.year, last_month_end.month, 1)

    categories = db.query(Category).filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None))
    ).all()
    cat_map = {c.id: c.name for c in categories}

    last_month_expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= last_month_start,
        Expense.date <= last_month_end,
    ).all()

    last_month_total = sum(float(e.amount) for e in last_month_expenses)
    last_month_cat_totals = defaultdict(float)
    for e in last_month_expenses:
        last_month_cat_totals[cat_map.get(e.category_id, "Other")] += float(e.amount)

    sub_audit = summary.get("subscription_audit")
    subs_list = [
        f"{s.merchant_or_service}: ₹{s.amount:,.0f}/mo"
        for s in (sub_audit.detected_subscriptions if sub_audit else [])
    ]

    budget_50 = summary.get("budget_50_30_20")
    b50_str = (
        f"{budget_50.needs_pct:.0f}% Needs (₹{budget_50.needs_spend:,.0f}), "
        f"{budget_50.wants_pct:.0f}% Wants (₹{budget_50.wants_spend:,.0f}), "
        f"{budget_50.savings_pct:.0f}% Savings (₹{budget_50.savings_spend:,.0f})"
        if budget_50 else "No data"
    )

    total_sub_recurring = sub_audit.total_monthly_recurring if sub_audit else 0.0
    ground_truth_facts = f"""GROUND-TRUTH FINANCIAL DATABASE RECORDS (STRICT FACT SHEET FOR LOGGED-IN USER):
- Current Month ({today.strftime('%B %Y')}):
  * Total Spend: ₹{summary.get('current_month_total', 0):,.2f} across {summary.get('total_expenses_count', 0)} transactions.
  * Category Breakdown: {summary.get('category_breakdown', {})}
  * Top Expenses: {summary.get('top_transactions', [])}
  * Active Budgets & Pacing: {summary.get('predictive_pacing_data', [])}
- Previous Month ({last_month_start.strftime('%B %Y')}):
  * Total Spend: ₹{last_month_total:,.2f}
  * Category Breakdown: {dict(last_month_cat_totals)}
- Active Subscriptions & Fixed Commitments: {subs_list} (Total: ₹{total_sub_recurring:,.0f}/mo)
- 50/30/20 Distribution: {b50_str}
"""

    system_instruction = (
        "You are ExpenseFlow Assistant, an intelligent, dedicated personal financial advisor strictly focused on ExpenseFlow. "
        "Answer the user's questions grounded STRICTLY in the provided database records.\n\n"
        "STRICT SCOPE & GUARDRAIL RULES:\n"
        "1. SCOPE VALIDATION: If the user asks ANY question that is NOT related to their personal finances, expenses, budgets, categories, savings, recurring subscriptions, or spending habits within ExpenseFlow (for example: coding, trivia, history, science, politics, weather, recipes, or random questions), you MUST politely decline and answer:\n"
        '   "I am **ExpenseFlow AI**, your dedicated personal financial assistant. I can only assist you with questions regarding your expenses, budgets, categories, spending habits, recurring subscriptions, and savings advice within ExpenseFlow.\n\nHow can I help you manage your finances today?"\n'
        "2. APPLICATION & FINANCIAL QUESTIONS: If the question IS related to ExpenseFlow or the user's finances, answer it directly, concisely, and accurately based on the facts provided.\n"
        "3. Always format currency in Indian Rupees (₹ INR).\n"
        "4. Do NOT hallucinate transactions or numbers not present in the fact sheet. If the user asks about an item or category they haven't logged, politely clarify that no matching records were found in their account.\n"
        "5. Keep answers concise, actionable, and formatted in clean markdown (with bolding, bullets, and short paragraphs).\n"
        "6. Suggest 3 short, relevant follow-up questions the user might want to ask next.\n"
        "7. Respond in valid JSON with this exact schema:\n"
        "{\n"
        '  "reply": "<Markdown formatted answer grounded in the numbers>",\n'
        '  "suggested_followups": ["<Question 1>", "<Question 2>", "<Question 3>"],\n'
        '  "data_points_referenced": ["<e.g. Current Month Total: ₹14,200>", "<Food & Dining: ₹4,500>"]\n'
        "}"
    )

    conversation_context = ""
    for msg in request.conversation_history[-4:]:  # last 4 turns
        conversation_context += f"{msg.role.upper()}: {msg.content}\n"
    conversation_context += f"USER: {request.message}\n"

    prompt = f"{ground_truth_facts}\n\nCONVERSATION HISTORY:\n{conversation_context}"

    provider = get_ai_provider()
    try:
        raw_json = provider.generate_structured_json(prompt=prompt, system_instruction=system_instruction)
        reply = raw_json.get("reply", "I've analyzed your financial data.")
        followups = raw_json.get("suggested_followups", [])
        if not followups:
            followups = ["Where did most of my money go this week?", "How can I reduce my recurring bills?", "Am I on track with my monthly budget?"]
        data_points = raw_json.get("data_points_referenced", [])

        return AIChatResponse(
            reply=reply,
            suggested_followups=followups[:3],
            data_points_referenced=data_points,
            provider_used=settings.AI_PROVIDER,
        )
    except Exception as e:
        logger.error(f"Failed to generate chat response: {e}")

        # Intelligent Question-Aware Fallback Engine
        user_msg = request.message.lower().strip()
        finance_keywords = {
            "spend", "spent", "money", "cost", "expense", "budget", "save", "saving", "food",
            "dining", "restaurant", "shopping", "subscription", "recurring", "50", "30", "20",
            "entertainment", "burn", "pacing", "highest", "top", "total", "netflix", "gym",
            "wifi", "bill", "utilities", "month", "week", "today", "rupee", "inr", "balance",
            "afford", "category", "categories", "habits", "track", "limit", "flow", "account"
        }

        has_finance_intent = any(kw in user_msg for kw in finance_keywords)
        current_total = summary.get("current_month_total", 0.0)
        category_breakdown = summary.get("category_breakdown", {})
        top_tx = summary.get("top_transactions", [])
        top_desc = top_tx[0]["description"] if top_tx else "None recorded"
        top_amt = top_tx[0]["amount"] if top_tx else 0.0

        if not has_finance_intent and len(user_msg.split()) > 1:
            # Out-of-scope query
            return AIChatResponse(
                reply=(
                    "I am **ExpenseFlow AI**, your dedicated personal financial assistant. "
                    "I can only assist you with questions regarding your expenses, budgets, categories, "
                    "spending habits, recurring subscriptions, and savings advice within ExpenseFlow.\n\n"
                    "How can I help you manage your finances today?"
                ),
                suggested_followups=[
                    "Where did most of my money go this month?",
                    "Check my current budget pacing",
                    "How can I save ₹3,000 more?",
                ],
                data_points_referenced=[],
                provider_used="rule-engine",
            )

        # Question-specific answers based on live database records
        if any(w in user_msg for w in ["food", "dining", "eat", "restaurant", "zomato", "swiggy"]):
            food_amt = sum(amt for cat, amt in category_breakdown.items() if any(f in cat.lower() for f in ["food", "dining", "restaurant", "grocery"]))
            reply = (
                f"Based on your logged transactions for **{today.strftime('%B %Y')}**:\n\n"
                f"- **Food & Dining Total**: ₹{food_amt:,.2f}\n"
                f"- This represents **{(food_amt / current_total * 100) if current_total > 0 else 0:.1f}%** of your total monthly spending.\n\n"
                "💡 *Tip: Cooking at home more often or reducing food deliveries could free up significant monthly savings.*"
            )
            data_points = [f"Food Spending: ₹{food_amt:,.2f}"]
        elif any(w in user_msg for w in ["subscription", "recurring", "netflix", "spotify", "gym", "wifi", "broadband"]):
            reply = (
                f"Here is your **Subscription Audit** for this month:\n\n"
                f"- **Active Subscriptions**: {len(subs_list)} detected\n"
                f"- **Total Monthly Recurring Overhead**: ₹{total_sub_recurring:,.2f}/month\n"
                f"- **Detected Services**: {', '.join(subs_list) if subs_list else 'No recurring subscriptions detected yet.'}\n\n"
                "💡 *Tip: Check for annual discount options or cancel unused streaming plans to save immediately.*"
            )
            data_points = [f"Total Recurring: ₹{total_sub_recurring:,.0f}/mo", f"Count: {len(subs_list)}"]
        elif any(w in user_msg for w in ["50/30/20", "50", "rule", "split", "ratio", "allocation"]):
            reply = (
                f"Under the **50/30/20 Budget Optimization Rule** for {today.strftime('%B %Y')}:\n\n"
                f"- **Needs (50% target)**: {b50_str}\n\n"
                f"💡 *{budget_50.rebalancing_advice if budget_50 else 'Log more categorized expenses to get a personalized distribution.'}*"
            )
            data_points = [b50_str]
        elif any(w in user_msg for w in ["budget", "pacing", "burn", "exhaust", "pace"]):
            pacing_alerts = summary.get("predictive_pacing_data", [])
            if pacing_alerts:
                p_info = pacing_alerts[0]
                reply = (
                    f"Here is your **Budget Pacing & Burn Rate Forecast**:\n\n"
                    f"- **Category**: {p_info.get('category', 'Overall')}\n"
                    f"- **Current Spend**: ₹{p_info.get('current_spend', 0):,.2f} of ₹{p_info.get('budget_limit', 0):,.2f}\n"
                    f"- **Daily Burn Rate**: ₹{p_info.get('daily_burn_rate', 0):,.2f}/day\n"
                    f"- **Safe Daily Limit**: ₹{p_info.get('safe_daily_ceiling', 0):,.2f}/day\n"
                    f"- **Pacing Status**: {p_info.get('pacing_status', 'safe').upper()}\n\n"
                    f"{p_info.get('alert_message', '')}"
                )
                data_points = [f"Burn Rate: ₹{p_info.get('daily_burn_rate', 0):,.0f}/day"]
            else:
                reply = (
                    f"You have spent **₹{current_total:,.2f}** this month across {summary.get('total_expenses_count', 0)} transactions. "
                    "You do not have any active budgets configured yet. Create a budget in the **Budgets** tab to enable predictive pacing forecasts!"
                )
                data_points = [f"Total Spent: ₹{current_total:,.2f}"]
        elif any(w in user_msg for w in ["top", "highest", "largest", "biggest", "most"]):
            top_cat = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "N/A"
            top_cat_amt = category_breakdown.get(top_cat, 0.0)
            reply = (
                f"Here is where most of your money went in **{today.strftime('%B %Y')}**:\n\n"
                f"- **Top Spending Category**: **{top_cat}** at **₹{top_cat_amt:,.2f}** ({(top_cat_amt / current_total * 100) if current_total > 0 else 0:.1f}% of total)\n"
                f"- **Single Largest Expense**: **{top_desc}** (₹{top_amt:,.2f})\n\n"
                "Would you like advice on how to reduce spending in this category?"
            )
            data_points = [f"Top Category: {top_cat} (₹{top_cat_amt:,.2f})", f"Top Item: {top_desc}"]
        elif any(w in user_msg for w in ["save", "saving", "tip", "reduce", "cut"]):
            saving_tips = summary.get("saving_tips", [])
            tip_text = "\n".join([f"- **{t['title']}**: {t['description']} *(Potential: ₹{t.get('estimated_monthly_savings', 0):,.0f}/mo)*" for t in saving_tips[:2]]) if saving_tips else "- Review recurring subscriptions and trim discretionary dining expenses."
            reply = (
                f"Here are your top personalized **Saving Opportunities** for this month:\n\n"
                f"{tip_text}\n\n"
                "Focus on small daily adjustments to hit your target monthly savings!"
            )
            data_points = [f"Current Month Spend: ₹{current_total:,.2f}"]
        else:
            top_cat = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "None"
            reply = (
                f"Here is your financial summary for **{today.strftime('%B %Y')}**:\n\n"
                f"- **Total Spend**: ₹{current_total:,.2f} ({summary.get('total_expenses_count', 0)} transactions)\n"
                f"- **Top Category**: {top_cat} (₹{category_breakdown.get(top_cat, 0):,.2f})\n"
                f"- **Largest Expense**: {top_desc} (₹{top_amt:,.2f})\n"
                f"- **Active Subscriptions**: {len(subs_list)} (₹{total_sub_recurring:,.0f}/mo)\n\n"
                "Ask me about your budget pacing, category details, or 50/30/20 breakdown!"
            )
            data_points = [f"Month Total: ₹{current_total:,.2f}"]

        return AIChatResponse(
            reply=reply,
            suggested_followups=[
                "Where did most of my money go this month?",
                "How much can I save on food and dining?",
                "Check my current budget pacing",
            ],
            data_points_referenced=data_points,
            provider_used="rule-engine",
        )
