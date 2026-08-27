from datetime import date as date_type
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from ..models.budget import Budget
from ..models.category import Category
from ..models.expense import Expense
from ..schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetStatusItem,
    OverallBudgetStatusResponse,
)
from ..core.exceptions import ResourceNotFoundException, BadRequestException


def get_budgets(
    db: Session,
    month: Optional[int] = None,
    year: Optional[int] = None,
    category_id: Optional[int] = None,
) -> List[Budget]:
    query = db.query(Budget).options(joinedload(Budget.category))

    if month is not None:
        query = query.filter(Budget.month == month)
    if year is not None:
        query = query.filter(Budget.year == year)
    if category_id is not None:
        query = query.filter(Budget.category_id == category_id)

    return query.order_by(Budget.year.desc(), Budget.month.desc()).all()


def get_budget_by_id(db: Session, budget_id: int) -> Budget:
    budget = (
        db.query(Budget)
        .options(joinedload(Budget.category))
        .filter(Budget.id == budget_id)
        .first()
    )
    if not budget:
        raise ResourceNotFoundException(
            detail=f"Budget with ID {budget_id} not found",
            error_code="BUDGET_NOT_FOUND",
        )
    return budget


def create_or_update_budget(db: Session, schema: BudgetCreate) -> Budget:
    # Verify category exists if provided
    if schema.category_id is not None:
        cat = db.query(Category).filter(Category.id == schema.category_id).first()
        if not cat:
            raise BadRequestException(
                detail=f"Category with ID {schema.category_id} does not exist",
                error_code="INVALID_CATEGORY",
            )

    # Check if budget already exists for this month, year, and category_id
    query = db.query(Budget).filter(
        Budget.month == schema.month,
        Budget.year == schema.year,
    )
    if schema.category_id is None:
        query = query.filter(Budget.category_id.is_(None))
    else:
        query = query.filter(Budget.category_id == schema.category_id)

    existing = query.first()

    if existing:
        existing.amount = schema.amount
        db.commit()
        db.refresh(existing)
        return get_budget_by_id(db, existing.id)

    budget = Budget(
        month=schema.month,
        year=schema.year,
        amount=schema.amount,
        category_id=schema.category_id,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return get_budget_by_id(db, budget.id)


def update_budget(db: Session, budget_id: int, schema: BudgetUpdate) -> Budget:
    budget = get_budget_by_id(db, budget_id)

    if schema.category_id is not None and schema.category_id != budget.category_id:
        cat = db.query(Category).filter(Category.id == schema.category_id).first()
        if not cat:
            raise BadRequestException(
                detail=f"Category with ID {schema.category_id} does not exist",
                error_code="INVALID_CATEGORY",
            )
        budget.category_id = schema.category_id

    if schema.amount is not None:
        budget.amount = schema.amount
    if schema.month is not None:
        budget.month = schema.month
    if schema.year is not None:
        budget.year = schema.year

    db.commit()
    db.refresh(budget)
    return get_budget_by_id(db, budget.id)


def delete_budget(db: Session, budget_id: int) -> None:
    budget = get_budget_by_id(db, budget_id)
    db.delete(budget)
    db.commit()


def get_budget_status(db: Session, month: int, year: int) -> OverallBudgetStatusResponse:
    # 1. Fetch budgets for the period
    budgets = get_budgets(db, month=month, year=year)

    # 2. Fetch expenses for the period grouped by category
    expense_query = db.query(
        Expense.category_id,
        func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("total_spent"),
    ).filter(
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year,
    ).group_by(Expense.category_id).all()

    category_spent_map = {cat_id: spent for cat_id, spent in expense_query}
    overall_spent = sum(category_spent_map.values(), Decimal("0.00"))

    overall_budget_item: Optional[BudgetStatusItem] = None
    category_budgets: List[BudgetStatusItem] = []

    for b in budgets:
        budget_amt = b.amount
        if b.category_id is None:
            # Overall monthly budget
            spent = overall_spent
            rem = budget_amt - spent
            pct = round(float(spent / budget_amt * 100), 2) if budget_amt > 0 else 0.0
            status_lvl = "exceeded" if pct > 100 else ("warning" if pct >= 80 else "ok")
            overall_budget_item = BudgetStatusItem(
                budget_id=b.id,
                category_id=None,
                category_name="Overall Budget",
                budget_amount=budget_amt,
                spent_amount=spent,
                remaining_amount=rem,
                percentage_used=pct,
                status_level=status_lvl,
            )
        else:
            cat_name = b.category.name if b.category else f"Category #{b.category_id}"
            spent = category_spent_map.get(b.category_id, Decimal("0.00"))
            rem = budget_amt - spent
            pct = round(float(spent / budget_amt * 100), 2) if budget_amt > 0 else 0.0
            status_lvl = "exceeded" if pct > 100 else ("warning" if pct >= 80 else "ok")
            category_budgets.append(
                BudgetStatusItem(
                    budget_id=b.id,
                    category_id=b.category_id,
                    category_name=cat_name,
                    budget_amount=budget_amt,
                    spent_amount=spent,
                    remaining_amount=rem,
                    percentage_used=pct,
                    status_level=status_lvl,
                )
            )

    return OverallBudgetStatusResponse(
        month=month,
        year=year,
        overall_budget=overall_budget_item,
        category_budgets=category_budgets,
    )
