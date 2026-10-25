"""API routes for Expense Tracker."""
import io
import csv
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    FinancialSummary,
    BudgetSet,
    BudgetResponse,
    HealthResponse,
)
from app import crud

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Check API server and database connectivity status."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"
    return {
        "status": "ok",
        "message": "Expense Tracker API is functioning properly.",
        "database": db_status,
    }


@router.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Expenses"],
    summary="Create a new expense",
)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense record with validated amount, category, and date."""
    return crud.create_expense(db=db, expense_in=expense_in)


@router.get(
    "/expenses",
    response_model=List[ExpenseResponse],
    tags=["Expenses"],
    summary="List expenses with filtering and sorting",
)
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in category or description"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query(
        "date_desc",
        pattern="^(date_desc|date_asc|amount_desc|amount_asc)$",
        description="Sort by date_desc, date_asc, amount_desc, or amount_asc",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Retrieve expense records with optional search, category filter, date range, and sorting."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be later than end_date.",
        )
    return crud.get_expenses(
        db=db,
        category=category,
        search=search,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/expenses/totals",
    response_model=FinancialSummary,
    tags=["Expenses"],
    summary="Get financial summaries and category breakdown",
)
def get_totals(
    start_date: Optional[date] = Query(None, description="Start date for summary calculations"),
    end_date: Optional[date] = Query(None, description="End date for summary calculations"),
    db: Session = Depends(get_db),
):
    """Calculate total expenses, count, average, highest category, and category-wise spending."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be later than end_date.",
        )
    return crud.get_financial_summary(db=db, start_date=start_date, end_date=end_date)


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    tags=["Expenses"],
    summary="Get expense by ID",
)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single expense."""
    expense = crud.get_expense_by_id(db=db, expense_id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found.",
        )
    return expense


@router.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    tags=["Expenses"],
    summary="Update an existing expense",
)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    """Update amount, category, date, or description of an existing expense."""
    expense = crud.get_expense_by_id(db=db, expense_id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found.",
        )
    return crud.update_expense(db=db, expense=expense, expense_in=expense_in)


@router.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_200_OK,
    tags=["Expenses"],
    summary="Delete an expense",
)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an existing expense by ID."""
    expense = crud.get_expense_by_id(db=db, expense_id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found.",
        )
    crud.delete_expense(db=db, expense=expense)
    return {"status": "success", "message": f"Expense {expense_id} deleted successfully."}


@router.get(
    "/expenses/export/csv",
    tags=["Export"],
    summary="Export filtered expenses to CSV",
)
def export_csv(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sort_by: Optional[str] = Query("date_desc"),
    db: Session = Depends(get_db),
):
    """Generate and stream a CSV file containing transactions matching filters."""
    expenses = crud.get_expenses(
        db=db,
        category=category,
        search=search,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        limit=5000,
    )

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Expense ID", "Amount (INR)", "Category", "Date", "Description"])

    for exp in expenses:
        writer.writerow([
            exp.id,
            f"{exp.amount:.2f}",
            exp.category,
            exp.date.isoformat(),
            exp.description or "",
        ])

    output.seek(0)
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
    )
    response.headers["Content-Disposition"] = "attachment; filename=expenses_export.csv"
    return response


@router.post(
    "/budgets",
    response_model=BudgetResponse,
    tags=["Budget"],
    summary="Set or update monthly budget",
)
def set_monthly_budget(budget_in: BudgetSet, db: Session = Depends(get_db)):
    """Save budget target for a specific month (YYYY-MM)."""
    crud.set_budget(db=db, month=budget_in.month, monthly_budget=budget_in.monthly_budget)
    return crud.get_budget_status(db=db, month=budget_in.month)


@router.get(
    "/budgets/{month}",
    response_model=BudgetResponse,
    tags=["Budget"],
    summary="Get budget status for a given month",
)
def get_monthly_budget(month: str, db: Session = Depends(get_db)):
    """Check budget utilization, remaining amount, and alert status for month YYYY-MM."""
    return crud.get_budget_status(db=db, month=month)
