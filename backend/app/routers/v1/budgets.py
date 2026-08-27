from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    OverallBudgetStatusResponse,
)
from ...services import budget_service

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
):
    """Fetch all budgets, optionally filtered by month, year, or category."""
    return budget_service.get_budgets(db, month=month, year=year, category_id=category_id)


@router.get("/status", response_model=OverallBudgetStatusResponse)
def get_budget_status(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month (defaults to current month)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Year (defaults to current year)"),
    db: Session = Depends(get_db),
):
    """Fetch real-time budget status and spending utilization percentage for a given month/year."""
    now = datetime.now(timezone.utc)
    m = month if month is not None else now.month
    y = year if year is not None else now.year
    return budget_service.get_budget_status(db, month=m, year=y)


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    """Create or update a budget target for a specific month, year, and category."""
    return budget_service.create_or_update_budget(db, payload)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, payload: BudgetUpdate, db: Session = Depends(get_db)):
    """Update an existing budget."""
    return budget_service.update_budget(db, budget_id, payload)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """Delete a budget goal."""
    budget_service.delete_budget(db, budget_id)
    return None
