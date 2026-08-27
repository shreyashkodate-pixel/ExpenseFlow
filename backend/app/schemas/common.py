from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
    error_code: str = Field(..., description="Machine-readable error code")
    status_code: int = Field(..., description="HTTP status code")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int = Field(..., ge=0, description="Total count of matching records")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
