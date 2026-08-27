from datetime import date as date_type
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from .expense import ExpenseResponse
from .budget import BudgetStatusItem


class CategorySpendingItem(BaseModel):
    category_id: int
    category_name: str
    amount: Decimal
    percentage: float
    expense_count: int


class DailySpendingItem(BaseModel):
    date: date_type
    amount: Decimal
    expense_count: int


class MonthlySpendingItem(BaseModel):
    month: int
    year: int
    month_name: str
    amount: Decimal
    expense_count: int


class DashboardSummaryResponse(BaseModel):
    current_month_spending: Decimal = Field(..., description="Total spent in current calendar month")
    total_expense_count: int = Field(..., description="Total number of expense entries in system")
    highest_expense: Optional[ExpenseResponse] = Field(None, description="Highest single expense in system")
    recent_expenses: List[ExpenseResponse] = Field([], description="5 most recent expenses")
    budget_status: Optional[BudgetStatusItem] = Field(None, description="Current month overall budget status")
    top_categories: List[CategorySpendingItem] = Field([], description="Top spending categories in current month")


class DailyAnalyticsResponse(BaseModel):
    date: date_type
    total_amount: Decimal
    expense_count: int
    by_category: List[CategorySpendingItem]


class MonthlyAnalyticsResponse(BaseModel):
    month: int
    year: int
    total_amount: Decimal
    expense_count: int
    daily_breakdown: List[DailySpendingItem]
    by_category: List[CategorySpendingItem]


class YearlyAnalyticsResponse(BaseModel):
    year: int
    total_amount: Decimal
    expense_count: int
    monthly_breakdown: List[MonthlySpendingItem]
    by_category: List[CategorySpendingItem]
