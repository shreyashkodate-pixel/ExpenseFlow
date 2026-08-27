from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    category = relationship("Category", back_populates="budgets")

    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="check_budget_month_valid"),
        CheckConstraint("amount > 0", name="check_budget_amount_positive"),
    )
