from datetime import date as date_type
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from ..models.expense import Expense
from ..models.category import Category
from ..schemas.expense import ExpenseCreate, ExpenseUpdate
from ..schemas.common import PaginatedResponse
from ..core.exceptions import ResourceNotFoundException, BadRequestException


def get_expenses(
    db: Session,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    amount_min: Optional[Decimal] = None,
    amount_max: Optional[Decimal] = None,
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
    sort: str = "date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Expense], int]:
    query = db.query(Expense).options(joinedload(Expense.category))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Expense.description.ilike(search_term),
                Expense.notes.ilike(search_term),
            )
        )

    if category_id is not None:
        query = query.filter(Expense.category_id == category_id)

    if payment_method:
        query = query.filter(Expense.payment_method.ilike(payment_method.strip()))

    if amount_min is not None:
        query = query.filter(Expense.amount >= amount_min)

    if amount_max is not None:
        query = query.filter(Expense.amount <= amount_max)

    if date_from is not None:
        query = query.filter(Expense.date >= date_from)

    if date_to is not None:
        query = query.filter(Expense.date <= date_to)

    total = query.count()

    # Sorting logic
    sort_column = getattr(Expense, sort, Expense.date)
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc(), Expense.id.asc())
    else:
        query = query.order_by(sort_column.desc(), Expense.id.desc())

    # Pagination
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total


def get_expense_by_id(db: Session, expense_id: int) -> Expense:
    expense = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.id == expense_id)
        .first()
    )
    if not expense:
        raise ResourceNotFoundException(
            detail=f"Expense with ID {expense_id} not found",
            error_code="EXPENSE_NOT_FOUND"
        )
    return expense


def create_expense(db: Session, schema: ExpenseCreate) -> Expense:
    # Verify category exists
    category = db.query(Category).filter(Category.id == schema.category_id).first()
    if not category:
        raise BadRequestException(
            detail=f"Category with ID {schema.category_id} does not exist",
            error_code="INVALID_CATEGORY"
        )

    expense = Expense(
        amount=schema.amount,
        category_id=schema.category_id,
        description=schema.description.strip(),
        notes=schema.notes.strip() if schema.notes else None,
        date=schema.date,
        payment_method=schema.payment_method.strip() if schema.payment_method else None,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return get_expense_by_id(db, expense.id)


def update_expense(db: Session, expense_id: int, schema: ExpenseUpdate) -> Expense:
    expense = get_expense_by_id(db, expense_id)

    if schema.category_id is not None and schema.category_id != expense.category_id:
        category = db.query(Category).filter(Category.id == schema.category_id).first()
        if not category:
            raise BadRequestException(
                detail=f"Category with ID {schema.category_id} does not exist",
                error_code="INVALID_CATEGORY"
            )
        expense.category_id = schema.category_id

    if schema.amount is not None:
        expense.amount = schema.amount
    if schema.description is not None:
        expense.description = schema.description.strip()
    if schema.notes is not None:
        expense.notes = schema.notes.strip() if schema.notes else None
    if schema.date is not None:
        expense.date = schema.date
    if schema.payment_method is not None:
        expense.payment_method = schema.payment_method.strip() if schema.payment_method else None

    db.commit()
    db.refresh(expense)
    return get_expense_by_id(db, expense.id)


def delete_expense(db: Session, expense_id: int) -> None:
    expense = get_expense_by_id(db, expense_id)
    db.delete(expense)
    db.commit()
