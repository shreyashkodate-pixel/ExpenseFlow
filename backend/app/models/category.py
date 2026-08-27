from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .expense import Expense
    from .budget import Budget


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="category")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="category")
