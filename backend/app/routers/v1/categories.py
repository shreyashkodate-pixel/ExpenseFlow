from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithCountResponse
from ...services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryWithCountResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch system starter categories plus user custom categories with user-scoped expense counts."""
    return category_service.get_categories_with_counts(db, user_id=current_user.id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new custom category for the authenticated user."""
    return category_service.create_category(db, payload, user_id=current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get category by ID if accessible to the authenticated user."""
    return category_service.get_category_by_id(db, category_id, user_id=current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update custom category name. System starter categories cannot be edited."""
    return category_service.update_category(db, category_id, payload, user_id=current_user.id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    reassign_to: Optional[int] = Query(None, description="Category ID to reassign expenses to if category is in use"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a custom category. System starter categories cannot be deleted."""
    category_service.delete_category(db, category_id, user_id=current_user.id, reassign_to_id=reassign_to)
    return None
