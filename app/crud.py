"""Database CRUD helper functions for Expense Tracker."""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.models import Expense, Budget
from app.schemas import ExpenseCreate, ExpenseUpdate


def get_expenses(
    db: Session,
    category: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: Optional[str] = "date_desc",
    skip: int = 0,
    limit: int = 500,
) -> List[Expense]:
    """Retrieve expenses with category filter, search, date range, and sorting."""
    query = db.query(Expense)

    if category and category.strip():
        query = query.filter(Expense.category.ilike(category.strip()))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Expense.category.ilike(term)) | (Expense.description.ilike(term))
        )

    if start_date:
        query = query.filter(Expense.date >= start_date)

    if end_date:
        query = query.filter(Expense.date <= end_date)

    if sort_by == "date_asc":
        query = query.order_by(asc(Expense.date), asc(Expense.id))
    elif sort_by == "amount_desc":
        query = query.order_by(desc(Expense.amount), desc(Expense.id))
    elif sort_by == "amount_asc":
        query = query.order_by(asc(Expense.amount), asc(Expense.id))
    else:  # default date_desc
        query = query.order_by(desc(Expense.date), desc(Expense.id))

    return query.offset(skip).limit(limit).all()


def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
    """Retrieve a single expense by ID."""
    return db.query(Expense).filter(Expense.id == expense_id).first()


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """Create a new expense record."""
    expense = Expense(
        amount=round(expense_in.amount, 2),
        category=expense_in.category.strip(),
        date=expense_in.date,
        description=expense_in.description.strip() if expense_in.description else None,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def update_expense(db: Session, expense: Expense, expense_in: ExpenseUpdate) -> Expense:
    """Update an existing expense record."""
    if expense_in.amount is not None:
        expense.amount = round(expense_in.amount, 2)
    if expense_in.category is not None:
        expense.category = expense_in.category.strip()
    if expense_in.date is not None:
        expense.date = expense_in.date
    if expense_in.description is not None:
        expense.description = expense_in.description.strip() if expense_in.description else None

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    """Delete an expense record."""
    db.delete(expense)
    db.commit()


def get_financial_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict:
    """Calculate overall total, transaction count, average expense, and category spending."""
    query = db.query(Expense)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    expenses = query.all()

    total_expenses = 0.0
    category_map = {}

    for exp in expenses:
        amt = round(float(exp.amount), 2)
        total_expenses += amt
        cat = exp.category
        if cat not in category_map:
            category_map[cat] = {"total": 0.0, "count": 0}
        category_map[cat]["total"] += amt
        category_map[cat]["count"] += 1

    total_expenses = round(total_expenses, 2)
    transaction_count = len(expenses)
    average_expense = round(total_expenses / transaction_count, 2) if transaction_count > 0 else 0.0

    category_list = []
    highest_category = None
    highest_amount = -1.0

    # Sort categories alphabetically or by spending descending
    for cat, data in sorted(category_map.items(), key=lambda item: item[1]["total"], reverse=True):
        cat_total = round(data["total"], 2)
        pct = round((cat_total / total_expenses * 100.0), 2) if total_expenses > 0 else 0.0
        category_list.append({
            "category": cat,
            "total": cat_total,
            "percentage": pct,
            "count": data["count"],
        })
        if cat_total > highest_amount:
            highest_amount = cat_total
            highest_category = cat

    return {
        "total_expenses": total_expenses,
        "transaction_count": transaction_count,
        "highest_spending_category": highest_category,
        "average_expense": average_expense,
        "categories": category_list,
    }


def set_budget(db: Session, month: str, monthly_budget: float) -> Budget:
    """Set or update a monthly budget."""
    existing = db.query(Budget).filter(Budget.month == month).first()
    if existing:
        existing.monthly_budget = round(monthly_budget, 2)
        db.commit()
        db.refresh(existing)
        return existing
    new_budget = Budget(month=month, monthly_budget=round(monthly_budget, 2))
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


def get_budget_status(db: Session, month: str) -> dict:
    """Calculate budget status against expenses for the specified month (YYYY-MM)."""
    budget_row = db.query(Budget).filter(Budget.month == month).first()
    monthly_budget = budget_row.monthly_budget if budget_row else 0.0

    # Total expenses in that month
    # Using SQLite strftime
    expenses = db.query(Expense).all()
    month_spent = 0.0
    for exp in expenses:
        if exp.date.strftime("%Y-%m") == month:
            month_spent += round(float(exp.amount), 2)

    month_spent = round(month_spent, 2)
    remaining = round(monthly_budget - month_spent, 2)
    is_exceeded = month_spent > monthly_budget if monthly_budget > 0 else False
    pct_used = round((month_spent / monthly_budget * 100.0), 2) if monthly_budget > 0 else 0.0

    return {
        "month": month,
        "monthly_budget": monthly_budget,
        "total_spent": month_spent,
        "remaining_budget": remaining,
        "is_exceeded": is_exceeded,
        "percentage_used": pct_used,
    }
