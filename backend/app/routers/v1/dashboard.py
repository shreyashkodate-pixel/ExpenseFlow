from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.analytics import DashboardSummaryResponse
from ...services import analytics_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Fetch high-level dashboard summary metrics: current month spend, expense count, highest expense, recent expenses, budget status, and top categories."""
    return analytics_service.get_dashboard_summary(db)
