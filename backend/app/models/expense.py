from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    description = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    category = relationship("Category", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_expense_amount_positive"),
    )
