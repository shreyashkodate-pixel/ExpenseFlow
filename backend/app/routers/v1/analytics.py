from datetime import date as date_type, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...schemas.analytics import (
    DailyAnalyticsResponse,
    MonthlyAnalyticsResponse,
    YearlyAnalyticsResponse,
    CategorySpendingItem,
)
from ...services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/daily", response_model=DailyAnalyticsResponse)
def get_daily_analytics(
    date: Optional[date_type] = Query(None, description="Target date (YYYY-MM-DD), defaults to today"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch daily total spending and category breakdown for the authenticated user."""
    target_date = date if date is not None else datetime.now(timezone.utc).date()
    return analytics_service.get_daily_analytics(db, target_date, user_id=current_user.id)


@router.get("/monthly", response_model=MonthlyAnalyticsResponse)
def get_monthly_analytics(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12), defaults to current month"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Year, defaults to current year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch monthly spending trend, daily breakdown, and category distribution for the authenticated user."""
    now = datetime.now(timezone.utc)
    m = month if month is not None else now.month
    y = year if year is not None else now.year
    return analytics_service.get_monthly_analytics(db, month=m, year=y, user_id=current_user.id)


@router.get("/yearly", response_model=YearlyAnalyticsResponse)
def get_yearly_analytics(
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Year, defaults to current year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch annual spending trends and month-by-month breakdown for the authenticated user."""
    y = year if year is not None else datetime.now(timezone.utc).year
    return analytics_service.get_yearly_analytics(db, year=y, user_id=current_user.id)


@router.get("/categories", response_model=List[CategorySpendingItem])
def get_category_analytics(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch category spending breakdown and percentage of total spend for the authenticated user."""
    return analytics_service.get_category_analytics(db, user_id=current_user.id, month=month, year=year)
