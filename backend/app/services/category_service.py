from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.category import Category
from ..models.expense import Expense
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryWithCountResponse
from ..core.exceptions import ResourceNotFoundException, BadRequestException


def get_categories_with_counts(db: Session) -> List[CategoryWithCountResponse]:
    # Query categories with expense count using left outer join
    results = (
        db.query(Category, func.count(Expense.id).label("expense_count"))
        .outerjoin(Expense, Category.id == Expense.category_id)
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


def get_category_by_id(db: Session, category_id: int) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ResourceNotFoundException(
            detail=f"Category with ID {category_id} not found",
            error_code="CATEGORY_NOT_FOUND"
        )
    return category


def create_category(db: Session, schema: CategoryCreate) -> Category:
    existing = db.query(Category).filter(func.lower(Category.name) == func.lower(schema.name.strip())).first()
    if existing:
        raise BadRequestException(
            detail=f"Category '{schema.name}' already exists",
            error_code="CATEGORY_ALREADY_EXISTS"
        )
    
    category = Category(name=schema.name.strip())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, schema: CategoryUpdate) -> Category:
    category = get_category_by_id(db, category_id)
    new_name = schema.name.strip()
    
    existing = (
        db.query(Category)
        .filter(func.lower(Category.name) == func.lower(new_name), Category.id != category_id)
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


def delete_category(db: Session, category_id: int, reassign_to_id: Optional[int] = None) -> None:
    category = get_category_by_id(db, category_id)
    
    expense_count = db.query(func.count(Expense.id)).filter(Expense.category_id == category_id).scalar() or 0

    if expense_count > 0:
        if reassign_to_id is None:
            raise BadRequestException(
                detail=f"Cannot delete category '{category.name}' because it has {expense_count} associated expenses. Specify 'reassign_to' to reassign them.",
                error_code="CATEGORY_IN_USE"
            )
        
        reassign_category = get_category_by_id(db, reassign_to_id)
        if reassign_category.id == category_id:
            raise BadRequestException(
                detail="Cannot reassign expenses to the category being deleted",
                error_code="INVALID_REASSIGNMENT"
            )
        
        # Reassign expenses
        db.query(Expense).filter(Expense.category_id == category_id).update(
            {Expense.category_id: reassign_to_id}, synchronize_session=False
        )

    db.delete(category)
    db.commit()
