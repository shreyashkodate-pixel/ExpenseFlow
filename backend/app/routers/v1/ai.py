import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.dependencies import get_current_user, rate_limit
from ...models.user import User
from ...schemas.ai import (
    AIRecommendationResponse,
    AIChatRequest,
    AIChatResponse,
    SubscriptionAuditResponse,
    Budget50_30_20,
)
from ...services import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Financial Intelligence"])


@router.get("/recommendations", response_model=AIRecommendationResponse)
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve personalized AI financial recommendations and spending insights.
    Strictly isolated to authenticated user. Cached per user for environment-configured duration.
    """
    return ai_service.get_ai_recommendations(db, current_user.id, force_refresh=False)


@router.post("/recommendations/refresh", response_model=AIRecommendationResponse)
def refresh_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _limit=Depends(rate_limit("ai:refresh", max_requests=5, window_seconds=60)),
):
    """
    Force clear cached recommendations and generate fresh AI insights.
    Rate limited to 5 requests per minute.
    """
    return ai_service.get_ai_recommendations(db, current_user.id, force_refresh=True)


@router.post("/chat", response_model=AIChatResponse)
def chat_with_assistant(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _limit=Depends(rate_limit("ai:chat", max_requests=15, window_seconds=60)),
):
    """
    Step 5: Interactive Conversational Financial Assistant (Structured RAG).
    Answers natural language queries grounded directly in the user's database records.
    Rate limited to 15 requests per minute.
    """
    return ai_service.chat_with_ai(db, current_user.id, request)


@router.get("/subscriptions", response_model=SubscriptionAuditResponse)
def get_subscription_audit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Step 3: Subscription & Recurring Commitments Audit.
    Identifies recurring subscriptions, calculates total commitment overhead, and provides cost-cutting tips.
    """
    summary = ai_service._get_user_spending_summary(db, current_user.id)
    return summary["subscription_audit"]


@router.get("/50-30-20", response_model=Budget50_30_20)
def get_50_30_20_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Step 4: 50/30/20 Budget Optimization Breakdown.
    Classifies monthly spending into Needs (50%), Wants (30%), and Savings (20%) with rebalancing advice.
    """
    summary = ai_service._get_user_spending_summary(db, current_user.id)
    return summary["budget_50_30_20"]
