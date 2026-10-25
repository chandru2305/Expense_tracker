"""Automated backend test suite for Expense Tracker API."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Create a temporary in-memory or file-isolated SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test_expenses.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Setup test tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Teardown test tables and remove file
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_expenses.db"):
        try:
            os.remove("test_expenses.db")
        except OSError:
            pass


@pytest.fixture
def db_session():
    # Clean tables before each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --- Tests ---

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"


def test_empty_database_totals(client):
    """Test /expenses/totals when no records exist."""
    response = client.get("/expenses/totals")
    assert response.status_code == 200
    data = response.json()
    assert data["total_expenses"] == 0.0
    assert data["transaction_count"] == 0
    assert data["average_expense"] == 0.0
    assert data["highest_spending_category"] is None
    assert data["categories"] == []


def test_create_valid_expense(client):
    """Test creating a valid expense."""
    payload = {
        "amount": 250.50,
        "category": "Food",
        "date": "2026-10-20",
        "description": "Lunch at cafe",
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["amount"] == 250.50
    assert data["category"] == "Food"
    assert data["date"] == "2026-10-20"
    assert data["description"] == "Lunch at cafe"


def test_validation_invalid_amounts(client):
    """Test that zero, negative, boolean, and non-numeric amounts are rejected."""
    # Zero amount
    res1 = client.post("/expenses", json={"amount": 0, "category": "Food", "date": "2026-10-20"})
    assert res1.status_code == 422

    # Negative amount
    res2 = client.post("/expenses", json={"amount": -50, "category": "Food", "date": "2026-10-20"})
    assert res2.status_code == 422

    # Non-numeric
    res3 = client.post("/expenses", json={"amount": "abc", "category": "Food", "date": "2026-10-20"})
    assert res3.status_code == 422

    # Boolean amount
    res4 = client.post("/expenses", json={"amount": True, "category": "Food", "date": "2026-10-20"})
    assert res4.status_code == 422


def test_validation_invalid_category(client):
    """Test empty and whitespace-only categories are rejected."""
    # Empty string
    res1 = client.post("/expenses", json={"amount": 100, "category": "", "date": "2026-10-20"})
    assert res1.status_code == 422

    # Whitespace only
    res2 = client.post("/expenses", json={"amount": 100, "category": "   ", "date": "2026-10-20"})
    assert res2.status_code == 422


def test_validation_invalid_date(client):
    """Test impossible calendar dates and bad formats."""
    # Invalid calendar date (Feb 30)
    res1 = client.post("/expenses", json={"amount": 100, "category": "Food", "date": "2026-02-30"})
    assert res1.status_code == 422

    # Missing date
    res2 = client.post("/expenses", json={"amount": 100, "category": "Food"})
    assert res2.status_code == 422


def test_update_expense(client):
    """Test updating amount and category of an existing expense."""
    res_create = client.post("/expenses", json={"amount": 100, "category": "Food", "date": "2026-10-20"})
    exp_id = res_create.json()["id"]

    res_update = client.put(f"/expenses/{exp_id}", json={"amount": 175.50, "category": "Dining"})
    assert res_update.status_code == 200
    data = res_update.json()
    assert data["amount"] == 175.50
    assert data["category"] == "Dining"
    assert data["date"] == "2026-10-20"


def test_update_unknown_expense(client):
    """Test updating a non-existent expense returns 404."""
    res = client.put("/expenses/99999", json={"amount": 50})
    assert res.status_code == 404


def test_delete_expense(client):
    """Test deleting an expense."""
    res_create = client.post("/expenses", json={"amount": 300, "category": "Bills", "date": "2026-10-20"})
    exp_id = res_create.json()["id"]

    res_del = client.delete(f"/expenses/{exp_id}")
    assert res_del.status_code == 200

    # Ensure it no longer exists
    res_get = client.get(f"/expenses/{exp_id}")
    assert res_get.status_code == 404


def test_delete_unknown_expense(client):
    """Test deleting a non-existent expense returns 404."""
    res = client.delete("/expenses/99999")
    assert res.status_code == 404


def test_acceptance_flow_and_totals(client):
    """
    Acceptance test specification:
    - Food expense: ₹250
    - Food expense: ₹150
    - Transport expense: ₹500
    Expected results:
    - Total expenses: ₹900
    - Transaction count: 3
    - Average expense: ₹300
    - Food total: ₹400
    - Transport total: ₹500
    """
    client.post("/expenses", json={"amount": 250.0, "category": "Food", "date": "2026-10-18"})
    client.post("/expenses", json={"amount": 150.0, "category": "Food", "date": "2026-10-19"})
    client.post("/expenses", json={"amount": 500.0, "category": "Transport", "date": "2026-10-20"})

    res = client.get("/expenses/totals")
    assert res.status_code == 200
    totals = res.json()

    assert totals["total_expenses"] == 900.0
    assert totals["transaction_count"] == 3
    assert totals["average_expense"] == 300.0
    assert totals["highest_spending_category"] == "Transport"

    cat_map = {c["category"]: c["total"] for c in totals["categories"]}
    assert cat_map["Food"] == 400.0
    assert cat_map["Transport"] == 500.0

    # Test search for Food
    res_search = client.get("/expenses?search=Food")
    assert res_search.status_code == 200
    assert len(res_search.json()) == 2

    # Test filter by Transport
    res_filter = client.get("/expenses?category=Transport")
    assert res_filter.status_code == 200
    assert len(res_filter.json()) == 1

    # Test sorting by amount desc
    res_sort = client.get("/expenses?sort_by=amount_desc")
    assert res_sort.status_code == 200
    items = res_sort.json()
    assert items[0]["amount"] == 500.0
    assert items[1]["amount"] == 250.0
    assert items[2]["amount"] == 150.0


def test_export_csv(client):
    """Test CSV export functionality."""
    client.post("/expenses", json={"amount": 120, "category": "Shopping", "date": "2026-10-20", "description": "Stationery"})
    res = client.get("/expenses/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    content = res.text
    assert "Expense ID,Amount (INR),Category,Date,Description" in content
    assert "120.00,Shopping,2026-10-20,Stationery" in content


def test_budget_workflow(client):
    """Test setting budget and checking utilization calculation."""
    client.post("/expenses", json={"amount": 4000, "category": "Rent", "date": "2026-10-05"})
    client.post("/expenses", json={"amount": 2000, "category": "Food", "date": "2026-10-10"})

    # Set budget of 5000 for 2026-10
    res_set = client.post("/budgets", json={"month": "2026-10", "monthly_budget": 5000.0})
    assert res_set.status_code == 200
    b_data = res_set.json()
    assert b_data["monthly_budget"] == 5000.0
    assert b_data["total_spent"] == 6000.0
    assert b_data["is_exceeded"] is True
    assert b_data["remaining_budget"] == -1000.0
