from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from .category import CategoryResponse


class BudgetBase(BaseModel):
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2000, le=2100, description="Year (e.g. 2026)")
    amount: Decimal = Field(..., gt=0, description="Budget target amount, must be positive")
    category_id: Optional[int] = Field(None, description="Category ID (null for overall budget)")


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000, le=2100)
    category_id: Optional[int] = None


class BudgetResponse(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetStatusItem(BaseModel):
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    category_name: str
    budget_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: float
    status_level: str = Field(..., description="'ok' (<80%), 'warning' (80-100%), 'exceeded' (>100%)")


class OverallBudgetStatusResponse(BaseModel):
    month: int
    year: int
    overall_budget: Optional[BudgetStatusItem] = None
    category_budgets: List[BudgetStatusItem] = []
