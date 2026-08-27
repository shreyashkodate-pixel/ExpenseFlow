from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Category name")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryWithCountResponse(CategoryResponse):
    expense_count: int = Field(0, description="Number of expenses associated with this category")
