from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithCountResponse
from ...services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryWithCountResponse])
def get_categories(db: Session = Depends(get_db)):
    """Fetch all categories with associated expense count."""
    return category_service.get_categories_with_counts(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    return category_service.create_category(db, payload)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID."""
    return category_service.get_category_by_id(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    """Update category name."""
    return category_service.update_category(db, category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    reassign_to: Optional[int] = Query(None, description="Category ID to reassign expenses to if category is in use"),
    db: Session = Depends(get_db)
):
    """Delete a category. If expenses reference this category, reassign_to parameter must be supplied."""
    category_service.delete_category(db, category_id, reassign_to_id=reassign_to)
    return None
