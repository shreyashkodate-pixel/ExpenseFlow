from datetime import date as date_type, datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .category import Category


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_expense_amount_positive"),
    )
