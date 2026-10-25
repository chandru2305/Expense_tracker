"""SQLAlchemy models for Expense Tracker."""
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, func
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    month = Column(String(7), unique=True, nullable=False)  # YYYY-MM
    monthly_budget = Column(Float, nullable=False)
