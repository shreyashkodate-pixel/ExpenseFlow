import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.dependencies import get_current_user, rate_limit
from ...models.user import User
from ...schemas.ai import AIRecommendationResponse
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
