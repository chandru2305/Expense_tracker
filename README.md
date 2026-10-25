# Expense Tracker Web Application & REST API

A reliable, responsive, full-stack Expense Tracker application developed with **FastAPI**, **SQLite**, **Vanilla HTML5/CSS3/JavaScript**, **Pydantic v2**, and **pytest**. Designed for academic and college project demonstrations, personal finance management, and portfolio evaluation.

---

## 🌟 Key Features

1. **Interactive Glassmorphism Dashboard**:
   - Live **Financial Summary Cards**: Total Spending, Transaction Count, Highest Spending Category, Average Expense.
   - **Category-wise Spending Breakdown**: Visual progress bars, total amounts per category, transaction counts, and exact percentage share.
   - **Transaction History**: Displays Expense ID, Category, formatted Amount (in Indian Rupees ₹), Date, and Description.
   - **Full CRUD Operations**:
     - **Add Expense**: Modal form with real-time validation and custom category support.
     - **Edit Expense**: Pre-fills existing data and updates records seamlessly.
     - **Delete Expense**: Confirmation dialog preventing accidental loss of data.
   - **Real-Time Filtering, Search & Sorting**:
     - Category filter (Food, Transport, Shopping, Education, Bills, Healthcare, Entertainment, Other, Custom).
     - Full-text search matching category names and descriptions.
     - Date range filter (start date and end date).
     - Sorting: Newest first, Oldest first, Highest amount, Lowest amount.
     - One-click Filter Reset.
   - **Monthly Budget Management**:
     - Configure monthly spending targets.
     - Real-time progress bar tracking budget utilization.
     - Automated alert banner when spending exceeds the monthly limit.
   - **CSV Data Export**: Export active or filtered transactions to standard CSV for offline spreadsheets.
   - **Accessibility & UX**:
     - Semantic HTML5, ARIA dialog roles, skip links, keyboard navigation (Escape to close modals).
     - Toast notifications for success and error alerts.
     - Complete loading, empty, and error state handling.

2. **Robust Backend REST API**:
   - FastAPI with automatic interactive documentation (**Swagger UI** at `/docs` and **ReDoc** at `/redoc`).
   - SQLite persistence with SQLAlchemy ORM using parameterized queries.
   - Strict Pydantic input validation (rejects <=0 amounts, NaN, infinity, booleans, empty strings, and invalid calendar dates).
   - Clean JSON error responses and health monitoring endpoint (`/health`).

---

## 🏗️ Project Architecture & Folder Structure

```
expense_tracker_api/
├── app/
│   ├── __init__.py
│   ├── database.py       # SQLite connection and session management
│   ├── models.py         # SQLAlchemy ORM models (Expense, Budget)
│   ├── schemas.py        # Pydantic v2 validation models
│   ├── crud.py           # Database operations & financial calculations
│   ├── routes.py         # REST API endpoints & CSV streaming
│   ├── main.py           # FastAPI entry point & static files mounting
│   └── static/
│       ├── index.html    # Semantic, accessible HTML5 dashboard
│       ├── style.css     # Premium dark-mode glassmorphism stylesheet
│       └── app.js        # Vanilla JS client (API calls, UI state, DOM)
├── tests/
│   ├── __init__.py
│   └── test_expenses.py  # 13 comprehensive pytest test cases
├── expenses.db           # SQLite persistent database
├── README.md             # Project documentation
├── PRESENTATION.md       # College viva presentation guide & Q&A
└── requirements.txt      # Python dependencies
```

---

## 🚀 Installation & Local Startup

### 1. Requirements
- Python 3.10+ (Verified on Python 3.13.2)
- Windows PowerShell or Command Prompt

### 2. Setup Virtual Environment (Optional but recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install fastapi uvicorn sqlalchemy pydantic pytest
```

### 4. Run the Application
Start the Uvicorn development server:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```

### 5. Access the Web Application
- **Interactive Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check API and database health status |
| `POST` | `/expenses` | Create a new expense |
| `GET` | `/expenses` | List expenses (supports `category`, `search`, `start_date`, `end_date`, `sort_by`, `skip`, `limit`) |
| `GET` | `/expenses/totals` | Aggregate financial calculations and category breakdown |
| `GET` | `/expenses/{expense_id}` | Fetch a single expense by ID |
| `PUT` | `/expenses/{expense_id}` | Update an existing expense record |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense record |
| `GET` | `/expenses/export/csv` | Export transactions as a CSV file |
| `POST` | `/budgets` | Set or update monthly budget |
| `GET` | `/budgets/{month}` | Get budget utilization and alert status for `YYYY-MM` |

### Sample Request: Create Expense
```http
POST /expenses HTTP/1.1
Content-Type: application/json

{
  "amount": 250.00,
  "category": "Food",
  "date": "2026-10-20",
  "description": "Lunch with team"
}
```

### Sample Response:
```json
{
  "id": 1,
  "amount": 250.0,
  "category": "Food",
  "date": "2026-10-20",
  "description": "Lunch with team"
}
```

---

## 🧪 Automated Testing

Automated tests run against an isolated SQLite test database to guarantee real data is never overwritten.

To run the complete test suite:
```powershell
python -m pytest -v
```

### Test Coverage Highlights:
- API health check connectivity.
- Empty database totals and edge-case divisions by zero.
- Valid expense creation and field integrity.
- Validation rejections: negative amounts, zero amounts, non-numeric strings, boolean values, empty categories, and impossible calendar dates (e.g. Feb 30).
- Updates and 404 responses for unknown records.
- Deletions and subsequent cascade recalculations.
- Complete acceptance scenario (Food: ₹250, Food: ₹150, Transport: ₹500 → Total ₹900, Average ₹300, Food ₹400, Transport ₹500).
- CSV export streaming.
- Budget creation, remaining balance, and threshold alerts.

---

## 🛡️ Security & Reliability Best Practices
- **No SQL Injection**: Fully parameterized queries via SQLAlchemy ORM.
- **Safe DOM Manipulation**: Client uses `textContent` and sanitized DOM rendering, eliminating XSS risks.
- **Transaction Safety**: Atomic database commits with rollback safety.
- **Input Sanitization**: Trims whitespace and enforces character boundaries.
