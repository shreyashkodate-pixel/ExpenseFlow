from datetime import datetime, date, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.expense import Expense
from app.models.category import Category
from app.models.budget import Budget
from app.core.config import settings
from app.services.ai.factory import get_ai_provider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.claude_provider import ClaudeProvider
import pytest
from app.services.ai_service import clear_ai_cache


@pytest.fixture(autouse=True)
def reset_cache():
    clear_ai_cache()
    yield
    clear_ai_cache()


def test_ai_provider_factory_switching():
    """Verify that the factory properly selects the provider based on environment variables."""
    with patch.object(settings, "AI_PROVIDER", "gemini"):
        provider = get_ai_provider()
        assert isinstance(provider, GeminiProvider)
        assert provider.model == "gemini-3.6-flash"

    with patch.object(settings, "AI_PROVIDER", "openai"):
        provider = get_ai_provider()
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o-mini"

    with patch.object(settings, "AI_PROVIDER", "claude"):
        provider = get_ai_provider()
        assert isinstance(provider, ClaudeProvider)
        assert provider.model == "claude-3-5-haiku-20241022"


def test_ai_recommendations_endpoint_and_cache(
    client: TestClient,
    db_session: Session,
    auth_user_a: dict,
):
    """Verify that the AI recommendations endpoint works, calls the provider, and caches properly."""
    user = auth_user_a["user"]
    auth_headers = auth_user_a["headers"]

    # 1. Fetch an existing seeded category
    cat = db_session.query(Category).first()
    assert cat is not None

    today = date.today()
    # Add expenses: recent surge
    for i in range(3):
        e = Expense(
            user_id=user["id"],
            category_id=cat.id,
            amount=600.0,
            date=today - timedelta(days=i),
            description="Restaurant meal",
            payment_method="UPI",
        )
        db_session.add(e)
    # Budget
    budget = Budget(
        user_id=user["id"],
        amount=5000.0,
        month=today.month,
        year=today.year,
    )
    db_session.add(budget)
    db_session.commit()

    mock_llm_json = {
        "financial_health_score": 82,
        "health_status": "Good",
        "headline": "Dining Out accounts for the majority of your weekly spend.",
        "spending_spikes": [
            {
                "category": "Dining Out",
                "surge_percentage": 42.0,
                "insight": "You spent 42% more on Dining Out this week compared to your average."
            }
        ],
        "saving_tips": [
            {
                "title": "Trim Dining Out Orders",
                "description": "Cutting down 2 food orders per week could save you approximately ₹3,500/month.",
                "estimated_monthly_savings": 3500.0,
                "category": "Dining Out"
            }
        ],
        "budget_warnings": [
            {
                "category": "Overall",
                "status": "warning",
                "message": "At your current pace, you will reach 80% of your ₹5,000 budget by next week."
            }
        ],
        "positive_habits": [
            "Good job maintaining an active monthly budget."
        ]
    }

    with patch("app.services.ai.gemini_provider.GeminiProvider.generate_structured_json", return_value=mock_llm_json) as mock_generate:
        # First call: should query provider
        res1 = client.get("/api/v1/ai/recommendations", headers=auth_headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["financial_health_score"] == 82
        assert data1["health_status"] == "Excellent"
        assert len(data1["spending_spikes"]) == 1
        assert data1["spending_spikes"][0]["category"] == "Dining Out"
        assert data1["spending_spikes"][0]["surge_percentage"] == 42.0
        assert len(data1["saving_tips"]) == 1
        assert data1["saving_tips"][0]["estimated_monthly_savings"] == 3500.0
        assert data1["cached"] is False
        assert mock_generate.call_count == 1

        # Second call: should serve from cache
        res2 = client.get("/api/v1/ai/recommendations", headers=auth_headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["cached"] is True
        # Provider should NOT have been called a second time
        assert mock_generate.call_count == 1

        # Force refresh: should bypass cache
        res3 = client.post("/api/v1/ai/recommendations/refresh", headers=auth_headers)
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["cached"] is False
        assert mock_generate.call_count == 2


def test_ai_recommendations_new_user_empty_state(client: TestClient, auth_user_b: dict):
    """Verify that a brand new user with no expenses gets a clean 'Getting Started' response without calling LLM."""
    auth_headers = auth_user_b["headers"]
    res = client.get("/api/v1/ai/recommendations", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["financial_health_score"] == 100
    assert data["health_status"] == "Getting Started"
    assert len(data["spending_spikes"]) == 0
    assert len(data["saving_tips"]) >= 1
    assert "Welcome to ExpenseFlow" in data["positive_habits"][0]


def test_predictive_budget_overspending_alerts(client: TestClient, auth_user_a: dict):
    """Verify predictive pacing, exhaustion forecasting, and daily ceiling calculations."""
    auth_headers = auth_user_a["headers"]
    today = datetime.now()

    # Create an overall monthly budget of ₹3,000
    b_res = client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={"month": today.month, "year": today.year, "amount": 3000.0, "category_id": None},
    )
    assert b_res.status_code in (200, 201)

    # Add rapid spending (2 expenses so count >= 2) to simulate high burn rate
    cat_res = client.get("/api/v1/categories", headers=auth_headers)
    cat_id = cat_res.json()[0]["id"]
    client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "amount": 1500.0,
            "category_id": cat_id,
            "date": today.strftime("%Y-%m-%d"),
            "description": "High velocity spending test 1",
        },
    )
    client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "amount": 1000.0,
            "category_id": cat_id,
            "date": today.strftime("%Y-%m-%d"),
            "description": "High velocity spending test 2",
        },
    )

    mock_llm_json = {
        "financial_health_score": 45,
        "health_status": "Needs Attention",
        "headline": "High burn rate detected on overall monthly budget.",
        "spending_spikes": [],
        "saving_tips": [],
        "predictive_budget_alerts": [
            {
                "category": "Overall",
                "alert_message": "At your current pace, you will exceed your ₹3,000 budget well before month-end.",
                "current_spend": 2500.0,
                "budget_limit": 3000.0,
                "daily_burn_rate": 150.0,
                "safe_daily_ceiling": 50.0,
                "pacing_status": "critical"
            }
        ],
        "budget_warnings": [],
        "positive_habits": [],
    }

    with patch("app.services.ai.gemini_provider.GeminiProvider.generate_structured_json", return_value=mock_llm_json):
        res = client.post("/api/v1/ai/recommendations/refresh", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data["predictive_budget_alerts"]) >= 1
        alert = next(a for a in data["predictive_budget_alerts"] if a["category"] == "Overall")
        assert alert["current_spend"] >= 2500.0
        assert alert["budget_limit"] == 3000.0
        assert alert["daily_burn_rate"] > 0
        assert alert["safe_daily_ceiling"] >= 0
        assert alert["pacing_status"] in ("critical", "caution", "exceeded")
        assert "3,000" in alert["alert_message"]
