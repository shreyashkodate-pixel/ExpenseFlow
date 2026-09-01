from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...schemas.analytics import DashboardSummaryResponse
from ...services import analytics_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardSummaryResponse)
@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch high-level dashboard summary metrics strictly for the authenticated user."""
    return analytics_service.get_dashboard_summary(db, user_id=current_user.id)
