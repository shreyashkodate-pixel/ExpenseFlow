from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .category import CategoryResponse


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Expense amount, must be greater than 0")
    category_id: int = Field(..., description="ID of the category")
    description: str = Field(..., min_length=1, max_length=50, description="Short description")
    notes: Optional[str] = Field(None, description="Detailed notes")
    date: date_type = Field(..., description="Date of expense")
    payment_method: Optional[str] = Field(None, max_length=30, description="Payment method used")

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            return None
        return v


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = None
    date: Optional[date_type] = None
    payment_method: Optional[str] = Field(None, max_length=30)


class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
