import calendar
from datetime import date as date_type, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from ..models.expense import Expense
from ..models.category import Category
from ..schemas.analytics import (
    DashboardSummaryResponse,
    DailyAnalyticsResponse,
    MonthlyAnalyticsResponse,
    YearlyAnalyticsResponse,
    CategorySpendingItem,
    DailySpendingItem,
    MonthlySpendingItem,
)
from ..schemas.expense import ExpenseResponse
from .budget_service import get_budget_status


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    now = datetime.now(timezone.utc)
    current_month = now.month
    current_year = now.year

    # 1. Current month spending
    current_month_spending = (
        db.query(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .filter(
            extract("month", Expense.date) == current_month,
            extract("year", Expense.date) == current_year,
        )
        .scalar()
        or Decimal("0.00")
    )

    # 2. Total expense count
    total_expense_count = db.query(func.count(Expense.id)).scalar() or 0

    # 3. Highest single expense
    highest_exp = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .order_by(Expense.amount.desc())
        .first()
    )
    highest_exp_resp = ExpenseResponse.model_validate(highest_exp) if highest_exp else None

    # 4. Recent 5 expenses
    recent_exps = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .order_by(Expense.date.desc(), Expense.id.desc())
        .limit(5)
        .all()
    )
    recent_exps_resp = [ExpenseResponse.model_validate(e) for e in recent_exps]

    # 5. Budget status for current month
    b_status = get_budget_status(db, month=current_month, year=current_year)
    overall_b_status = b_status.overall_budget

    # 6. Top category spending for current month
    top_cats = get_category_analytics(db, month=current_month, year=current_year)[:5]

    return DashboardSummaryResponse(
        current_month_spending=current_month_spending,
        total_expense_count=total_expense_count,
        highest_expense=highest_exp_resp,
        recent_expenses=recent_exps_resp,
        budget_status=overall_b_status,
        top_categories=top_cats,
    )


def get_category_analytics(
    db: Session, month: Optional[int] = None, year: Optional[int] = None
) -> List[CategorySpendingItem]:
    query = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("amount"),
        func.count(Expense.id).label("expense_count"),
    ).join(Expense, Category.id == Expense.category_id)

    if month is not None:
        query = query.filter(extract("month", Expense.date) == month)
    if year is not None:
        query = query.filter(extract("year", Expense.date) == year)

    results = query.group_by(Category.id, Category.name).order_by(func.sum(Expense.amount).desc()).all()

    total_amount = sum((r.amount for r in results), Decimal("0.00"))

    cat_items = []
    for r in results:
        pct = round(float(r.amount / total_amount * 100), 2) if total_amount > 0 else 0.0
        cat_items.append(
            CategorySpendingItem(
                category_id=r.category_id,
                category_name=r.category_name,
                amount=r.amount,
                percentage=pct,
                expense_count=r.expense_count,
            )
        )
    return cat_items


def get_daily_analytics(db: Session, target_date: date_type) -> DailyAnalyticsResponse:
    # Expenses for date
    expenses = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.date == target_date)
        .all()
    )

    total_amount = sum((e.amount for e in expenses), Decimal("0.00"))
    expense_count = len(expenses)

    # Category breakdown for date
    cat_map = {}
    for e in expenses:
        cat_id = e.category_id
        cat_name = e.category.name if e.category else "Unassigned"
        if cat_id not in cat_map:
            cat_map[cat_id] = {"name": cat_name, "amount": Decimal("0.00"), "count": 0}
        cat_map[cat_id]["amount"] += e.amount
        cat_map[cat_id]["count"] += 1

    by_category = []
    for cat_id, data in cat_map.items():
        pct = round(float(data["amount"] / total_amount * 100), 2) if total_amount > 0 else 0.0
        by_category.append(
            CategorySpendingItem(
                category_id=cat_id,
                category_name=data["name"],
                amount=data["amount"],
                percentage=pct,
                expense_count=data["count"],
            )
        )
    by_category.sort(key=lambda x: x.amount, reverse=True)

    return DailyAnalyticsResponse(
        date=target_date,
        total_amount=total_amount,
        expense_count=expense_count,
        by_category=by_category,
    )


def get_monthly_analytics(db: Session, month: int, year: int) -> MonthlyAnalyticsResponse:
    # 1. Total & count for month
    total_amount = (
        db.query(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .filter(
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .scalar()
        or Decimal("0.00")
    )

    expense_count = (
        db.query(func.count(Expense.id))
        .filter(
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .scalar()
        or 0
    )

    # 2. Daily breakdown for all calendar days of the month
    daily_results = (
        db.query(
            Expense.date,
            func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("amount"),
            func.count(Expense.id).label("expense_count"),
        )
        .filter(
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .group_by(Expense.date)
        .all()
    )

    daily_map = {r.date: r for r in daily_results}
    num_days = calendar.monthrange(year, month)[1]
    daily_breakdown = []

    for day in range(1, num_days + 1):
        d_date = date_type(year, month, day)
        if d_date in daily_map:
            daily_breakdown.append(
                DailySpendingItem(
                    date=d_date,
                    amount=daily_map[d_date].amount,
                    expense_count=daily_map[d_date].expense_count,
                )
            )
        else:
            daily_breakdown.append(
                DailySpendingItem(
                    date=d_date,
                    amount=Decimal("0.00"),
                    expense_count=0,
                )
            )

    # 3. Category breakdown
    by_category = get_category_analytics(db, month=month, year=year)

    return MonthlyAnalyticsResponse(
        month=month,
        year=year,
        total_amount=total_amount,
        expense_count=expense_count,
        daily_breakdown=daily_breakdown,
        by_category=by_category,
    )


def get_yearly_analytics(db: Session, year: int) -> YearlyAnalyticsResponse:
    # 1. Total & count for year
    total_amount = (
        db.query(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
        .filter(extract("year", Expense.date) == year)
        .scalar()
        or Decimal("0.00")
    )

    expense_count = (
        db.query(func.count(Expense.id))
        .filter(extract("year", Expense.date) == year)
        .scalar()
        or 0
    )

    # 2. Monthly breakdown
    monthly_results = (
        db.query(
            extract("month", Expense.date).label("month"),
            func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("amount"),
            func.count(Expense.id).label("expense_count"),
        )
        .filter(extract("year", Expense.date) == year)
        .group_by(extract("month", Expense.date))
        .order_by(extract("month", Expense.date).asc())
        .all()
    )

    monthly_breakdown = []
    for r in monthly_results:
        m_int = int(r.month)
        m_name = calendar.month_name[m_int]
        monthly_breakdown.append(
            MonthlySpendingItem(
                month=m_int,
                year=year,
                month_name=m_name,
                amount=r.amount,
                expense_count=r.expense_count,
            )
        )

    # 3. Category breakdown
    by_category = get_category_analytics(db, month=None, year=year)

    return YearlyAnalyticsResponse(
        year=year,
        total_amount=total_amount,
        expense_count=expense_count,
        monthly_breakdown=monthly_breakdown,
        by_category=by_category,
    )
