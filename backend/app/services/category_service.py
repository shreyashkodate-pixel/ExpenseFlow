from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.category import Category
from ..models.expense import Expense
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryWithCountResponse
from ..core.exceptions import ResourceNotFoundException, BadRequestException, ForbiddenException


def get_categories_with_counts(db: Session, user_id: int) -> List[CategoryWithCountResponse]:
    """
    Query system default categories (user_id is None) + user's custom categories (user_id == user_id).
    Calculates expense counts scoped strictly to the current user's expenses.
    """
    # Left outer join with Expense filtered to the current user's expenses
    results = (
        db.query(
            Category,
            func.count(Expense.id).label("expense_count")
        )
        .outerjoin(
            Expense,
            and_(
                Category.id == Expense.category_id,
                Expense.user_id == user_id
            )
        )
        .filter(
            (Category.user_id.is_(None)) | (Category.user_id == user_id)
        )
        .group_by(Category.id)
        .order_by(Category.name.asc())
        .all()
    )

    categories = []
    for cat, count in results:
        cat_resp = CategoryWithCountResponse(
            id=cat.id,
            name=cat.name,
            created_at=cat.created_at,
            expense_count=count,
        )
        categories.append(cat_resp)
    return categories


def get_category_by_id(db: Session, category_id: int, user_id: Optional[int] = None) -> Category:
    """Retrieve category accessible to user (system or owned)."""
    query = db.query(Category).filter(Category.id == category_id)
    if user_id is not None:
        query = query.filter((Category.user_id.is_(None)) | (Category.user_id == user_id))
    category = query.first()

    if not category:
        raise ResourceNotFoundException(
            detail=f"Category with ID {category_id} not found",
            error_code="CATEGORY_NOT_FOUND"
        )
    return category


def create_category(db: Session, schema: CategoryCreate, user_id: int) -> Category:
    """Create a new custom category for the authenticated user."""
    cleaned_name = schema.name.strip()
    existing = db.query(Category).filter(
        func.lower(Category.name) == func.lower(cleaned_name),
        (Category.user_id.is_(None) | (Category.user_id == user_id))
    ).first()
    if existing:
        raise BadRequestException(
            detail=f"Category '{cleaned_name}' already exists",
            error_code="CATEGORY_ALREADY_EXISTS"
        )

    category = Category(name=cleaned_name, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, schema: CategoryUpdate, user_id: int) -> Category:
    """Update custom category verifying ownership. System categories cannot be modified."""
    category = get_category_by_id(db, category_id, user_id)

    if category.user_id is None:
        raise ForbiddenException(
            detail="System starter categories cannot be modified",
            error_code="SYSTEM_CATEGORY_IMMUTABLE"
        )

    if category.user_id != user_id:
        raise ForbiddenException(
            detail="You do not have permission to modify this category",
            error_code="FORBIDDEN"
        )

    new_name = schema.name.strip()
    existing = (
        db.query(Category)
        .filter(
            func.lower(Category.name) == func.lower(new_name),
            Category.id != category_id,
            (Category.user_id.is_(None) | (Category.user_id == user_id))
        )
        .first()
    )
    if existing:
        raise BadRequestException(
            detail=f"Category '{new_name}' already exists",
            error_code="CATEGORY_ALREADY_EXISTS"
        )

    category.name = new_name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, user_id: int, reassign_to_id: Optional[int] = None) -> None:
    """Delete a user custom category. System categories cannot be deleted."""
    category = get_category_by_id(db, category_id, user_id)

    if category.user_id is None:
        raise ForbiddenException(
            detail="System starter categories cannot be deleted",
            error_code="SYSTEM_CATEGORY_IMMUTABLE"
        )

    if category.user_id != user_id:
        raise ForbiddenException(
            detail="You do not have permission to delete this category",
            error_code="FORBIDDEN"
        )

    expense_count = (
        db.query(func.count(Expense.id))
        .filter(Expense.category_id == category_id, Expense.user_id == user_id)
        .scalar()
        or 0
    )

    if expense_count > 0:
        if reassign_to_id is None:
            raise BadRequestException(
                detail=f"Cannot delete category '{category.name}' because it has {expense_count} associated expenses. Specify 'reassign_to' to reassign them.",
                error_code="CATEGORY_IN_USE"
            )

        reassign_category = get_category_by_id(db, reassign_to_id, user_id)
        if reassign_category.id == category_id:
            raise BadRequestException(
                detail="Cannot reassign expenses to the category being deleted",
                error_code="INVALID_REASSIGNMENT"
            )

        # Reassign expenses owned by this user
        db.query(Expense).filter(
            Expense.category_id == category_id,
            Expense.user_id == user_id
        ).update(
            {Expense.category_id: reassign_to_id}, synchronize_session=False
        )

    db.delete(category)
    db.commit()
