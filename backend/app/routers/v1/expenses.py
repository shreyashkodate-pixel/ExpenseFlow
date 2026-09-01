from datetime import date as date_type
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from ...schemas.common import PaginatedResponse
from ...services import expense_service, export_service
from ...core.exceptions import BadRequestException

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=PaginatedResponse[ExpenseResponse])
def get_expenses(
    search: Optional[str] = Query(None, description="Search term for description or notes"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    amount_min: Optional[Decimal] = Query(None, ge=0, description="Minimum amount filter"),
    amount_max: Optional[Decimal] = Query(None, ge=0, description="Maximum amount filter"),
    date_from: Optional[date_type] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[date_type] = Query(None, description="End date filter (YYYY-MM-DD)"),
    sort: str = Query("date", description="Sort field: date, amount, description"),
    order: str = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch paginated expenses strictly scoped to the authenticated user."""
    items, total = expense_service.get_expenses(
        db=db,
        user_id=current_user.id,
        search=search,
        category_id=category_id,
        payment_method=payment_method,
        amount_min=amount_min,
        amount_max=amount_max,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new expense record owned by the authenticated user."""
    return expense_service.create_expense(db, payload, current_user.id)


@router.get("/export")
def export_expenses(
    format: str = Query("csv", description="Export format: csv or pdf"),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    payment_method: Optional[str] = Query(None),
    amount_min: Optional[Decimal] = Query(None),
    amount_max: Optional[Decimal] = Query(None),
    date_from: Optional[date_type] = Query(None),
    date_to: Optional[date_type] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export the authenticated user's filtered expenses as a CSV or PDF file stream."""
    items, _ = expense_service.get_expenses(
        db=db,
        user_id=current_user.id,
        search=search,
        category_id=category_id,
        payment_method=payment_method,
        amount_min=amount_min,
        amount_max=amount_max,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
    )

    fmt = format.lower().strip()
    if fmt == "csv":
        csv_content = export_service.generate_csv_export(items)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=expenses_export.csv"},
        )
    elif fmt == "pdf":
        pdf_bytes = export_service.generate_pdf_export(items)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=expenses_export.pdf"},
        )
    else:
        raise BadRequestException(
            detail=f"Unsupported export format '{format}'. Supported formats: csv, pdf",
            error_code="UNSUPPORTED_FORMAT",
        )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get expense details by ID verifying ownership."""
    return expense_service.get_expense_by_id(db, expense_id, current_user.id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update expense details verifying ownership."""
    return expense_service.update_expense(db, expense_id, payload, current_user.id)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete expense record verifying ownership."""
    expense_service.delete_expense(db, expense_id, current_user.id)
    return None
