"""Pydantic validation schemas for Expense Tracker API."""
import datetime
from typing import Optional, List, Dict
import math
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ExpenseBase(BaseModel):
    amount: float = Field(..., description="Expense amount in INR (> 0)")
    category: str = Field(..., description="Category of the expense")
    date: datetime.date = Field(..., description="Date of the expense (YYYY-MM-DD)")
    description: Optional[str] = Field(None, max_length=255, description="Optional note or description")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v) -> float:
        if v is None:
            raise ValueError("Amount is required.")
        # Reject booleans that evaluate to float or int in python
        if isinstance(v, bool):
            raise ValueError("Amount cannot be a boolean.")
        try:
            val = float(v)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number.")
        if math.isnan(val) or math.isinf(val):
            raise ValueError("Amount must be a finite number.")
        if val <= 0:
            raise ValueError("Amount must be strictly greater than zero.")
        # Ensure precision is rounded to 2 decimal places
        return round(val, 2)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Category cannot be empty or whitespace only.")
        cleaned = v.strip()
        if len(cleaned) > 100:
            raise ValueError("Category name cannot exceed 100 characters.")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, description="Updated amount (> 0)")
    category: Optional[str] = Field(None, description="Updated category")
    date: Optional[datetime.date] = Field(None, description="Updated date (YYYY-MM-DD)")
    description: Optional[str] = Field(None, max_length=255, description="Updated description")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        if v is not None:
            if isinstance(v, bool):
                raise ValueError("Amount cannot be a boolean.")
            try:
                val = float(v)
            except (ValueError, TypeError):
                raise ValueError("Amount must be a valid number.")
            if math.isnan(val) or math.isinf(val):
                raise ValueError("Amount must be a finite number.")
            if val <= 0:
                raise ValueError("Amount must be strictly greater than zero.")
            return round(val, 2)
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Category cannot be empty or whitespace only.")
            cleaned = v.strip()
            if len(cleaned) > 100:
                raise ValueError("Category name cannot exceed 100 characters.")
            return cleaned
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class ExpenseResponse(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategorySpending(BaseModel):
    category: str
    total: float
    percentage: float
    count: int


class FinancialSummary(BaseModel):
    total_expenses: float
    transaction_count: int
    highest_spending_category: Optional[str]
    average_expense: float
    categories: List[CategorySpending]


class BudgetSet(BaseModel):
    month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Target month YYYY-MM")
    monthly_budget: float = Field(..., gt=0, description="Monthly budget limit in INR")

    @field_validator("monthly_budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v) or v <= 0:
            raise ValueError("Monthly budget must be a positive finite number.")
        return round(float(v), 2)


class BudgetResponse(BaseModel):
    month: str
    monthly_budget: float
    total_spent: float
    remaining_budget: float
    is_exceeded: bool
    percentage_used: float

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    message: str
    database: str
