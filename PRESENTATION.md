# Expense Tracker — College Project Presentation & Viva Guide

## 1. Project Introduction
The **Expense Tracker Web Application** is a full-stack personal finance system engineered with Python (FastAPI), SQLite, and a modern Vanilla HTML5/CSS3/JavaScript frontend. It enables users to record, categorize, inspect, analyze, and manage personal expenses, budget constraints, and spending trends with real-time feedback and mathematical precision.

---

## 2. Problem Statement
Individuals frequently struggle to manage personal budgets due to fragmented spending records, lack of categorized visibility, and difficult-to-use software. Many tools require heavyweight setups or cloud subscriptions. This project solves that problem by providing a lightweight, responsive, locally persistent application with zero unnecessary external dependencies and instant analytics.

---

## 3. Technology Stack & Architecture

- **Backend**: Python 3.13 / FastAPI (Asynchronous REST API, OpenAPI/Swagger auto-generation).
- **Validation**: Pydantic v2 (Strict schemas, type coercion prevention, date validation).
- **Database**: SQLite with SQLAlchemy ORM (ACID-compliant, zero-configuration embedded persistence).
- **Frontend**: Vanilla HTML5, modern CSS3 (Custom Properties, Glassmorphism, CSS Grid & Flexbox), Vanilla ES6 JavaScript (Fetch API, DOM manipulation).
- **Testing**: pytest & FastAPI TestClient.

### Architectural Diagram
```
[ Browser / Client ]
      │
      ▼  (HTTP / JSON)
[ FastAPI Application (app.main) ]
      ├─► [ Static File Server (/static, /) ]
      ├─► [ Pydantic Request Validation (app.schemas) ]
      ├─► [ REST Endpoints Router (app.routes) ]
      └─► [ CRUD & Calculations Layer (app.crud) ]
                │
                ▼  (SQLAlchemy ORM)
      [ SQLite Database (expenses.db) ]
```

---

## 4. Two-Minute Viva Presentation Script

> *"Good morning/afternoon, evaluators. Today I am presenting my full-stack Expense Tracker project, built using FastAPI, SQLite, and vanilla web standards.*
>
> *The application tackles personal finance tracking by providing an intuitive, responsive dashboard alongside a high-performance REST API. As you can see on the dashboard, users are immediately greeted by four core financial summary cards: Total Expenses, Transaction Count, Highest Spending Category, and Average Expense.*
>
> *When a user adds, edits, or deletes an expense, all data is validated on both frontend and backend using Pydantic. Notice that the backend strictly prevents zero or negative amounts, boolean types, and invalid calendar dates.*
>
> *Our dashboard dynamically computes category-wise spending with visual progress bars and exact percentage allocations. Users can filter expenses by category, search by note or description, restrict date ranges, sort by date or amount, and export their active transactions to a CSV spreadsheet.*
>
> *Additionally, we implemented a Monthly Budget feature that tracks spending against a configured budget limit and warns the user when spending exceeds threshold limits.*
>
> *The system is covered by an automated pytest suite running against an isolated test database, ensuring that data persistence and calculation formulas are 100% mathematically verified. Thank you."*

---

## 5. Live Demonstration Checklist

1. **Dashboard Load**: Open `http://127.0.0.1:8000/` and show current date, header, and clean summary state.
2. **Swagger Docs**: Click "Swagger Docs" button in the header or navigate to `/docs` to display interactive API documentation.
3. **Add Expenses**:
   - Add Food: ₹250.
   - Add Food: ₹150.
   - Add Transport: ₹500.
4. **Inspect Calculations**:
   - Total Expenses: ₹900.00
   - Transaction Count: 3
   - Average Expense: ₹300.00
   - Category Breakdown: Food ₹400.00 (44.4%), Transport ₹500.00 (55.6%).
5. **Search & Filter**:
   - Type "Food" into Search box -> shows 2 rows.
   - Select "Transport" from Category dropdown -> shows 1 row.
   - Click "Reset" -> restores full list.
6. **Sort**:
   - Select "Highest Amount" -> ₹500 row appears at the top.
7. **Edit**:
   - Click "Edit" on the ₹150 transaction, change to ₹200.
   - Confirm Total updates to ₹950.00.
8. **Delete**:
   - Click "Delete" on the ₹500 transaction -> confirmation dialog appears.
   - Confirm deletion -> Total updates to ₹450.00.
9. **Budget Tracking**:
   - Set monthly budget of ₹400.00 for current month.
   - Notice the spending (₹450.00) triggers the red overspent warning banner.
10. **CSV Export**:
    - Click "Export CSV" -> download `expenses_export.csv` and inspect contents.
11. **Automated Testing**:
    - In terminal run `python -m pytest -v` -> 13 passing tests.

---

## 6. Top 10 Technical Questions & Answers for Viva

### Q1: Why did you choose FastAPI over Flask or Django?
**Answer**: FastAPI offers superior performance, built-in asynchronous capabilities, native Pydantic validation, and automatic OpenAPI/Swagger documentation generation, making it more modern, faster to build, and less boilerplate-heavy than Flask or Django.

### Q2: How does the application prevent SQL Injection?
**Answer**: By using SQLAlchemy ORM and parameterized queries. No queries are built using raw string concatenation or interpolation, neutralizing SQL injection vectors.

### Q3: How do you handle Cross-Site Scripting (XSS) on the frontend?
**Answer**: In `app.js`, user-controlled data is inserted into the DOM strictly via `textContent` or sanitized HTML escaping functions rather than unchecked `innerHTML`.

### Q4: How is floating-point inaccuracy handled in monetary calculations?
**Answer**: We enforce strict rounding (`round(val, 2)`) on both input insertion and summary aggregations, preventing floating-point drift like `0.30000000000000004`.

### Q5: What happens if the database is empty? Does it throw a division-by-zero error?
**Answer**: No. In `crud.py`, the average is calculated using a ternary condition: `total / count if count > 0 else 0.0`. Similarly, category percentages check if `total_expenses > 0`.

### Q6: How does the system handle concurrent database requests in SQLite?
**Answer**: SQLite handles concurrency at file level, and in FastAPI we instantiate SQLAlchemy sessions with `connect_args={"check_same_thread": False}` and wrap sessions in a dependency generator (`get_db`) that ensures each request receives its own session and closes it in a `finally` block.

### Q7: Why use an isolated database in automated tests?
**Answer**: To adhere to testing best practices: tests must be deterministic, reproducible, and run in isolation without modifying or corrupting real user production data.

### Q8: What validation occurs if a client submits an invalid date like February 30?
**Answer**: Pydantic's `datetime.date` parser validates calendar semantics and immediately returns HTTP 422 Unprocessable Entity with a descriptive error message.

### Q9: How are modals made accessible to keyboard users?
**Answer**: Modals have `role="dialog"`, `aria-modal="true"`, focus autofocusing on the first input, an Escape key listener that closes active modals, and distinct focus outlines.

### Q10: How could this application be scaled for multi-user production?
**Answer**: By adding JWT-based user authentication, migrating the SQLite database to PostgreSQL with connection pooling, and deploying the containerized FastAPI app behind an Nginx reverse proxy.
