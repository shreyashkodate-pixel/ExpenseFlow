def test_dashboard_summary_endpoint(client):
    cats = client.get("/api/v1/categories").json()
    food_id = next(c["id"] for c in cats if c["name"] == "Food")
    transport_id = next(c["id"] for c in cats if c["name"] == "Transport")

    # Add expenses
    client.post("/api/v1/expenses", json={
        "amount": 500.0,
        "category_id": food_id,
        "description": "Groceries",
        "date": "2026-08-01"
    })
    client.post("/api/v1/expenses", json={
        "amount": 1500.0,
        "category_id": transport_id,
        "description": "Flight Ticket",
        "date": "2026-08-10"
    })

    # Fetch dashboard summary
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 200
    data = res.json()

    assert data["total_expense_count"] == 2
    assert float(data["highest_expense"]["amount"]) == 1500.0
    assert len(data["recent_expenses"]) == 2
    assert len(data["top_categories"]) == 2
    assert data["top_categories"][0]["category_name"] == "Transport"


def test_daily_monthly_yearly_analytics(client):
    cats = client.get("/api/v1/categories").json()
    rent_id = next(c["id"] for c in cats if c["name"] == "Rent")

    client.post("/api/v1/expenses", json={
        "amount": 12000.0,
        "category_id": rent_id,
        "description": "Monthly Apartment Rent",
        "date": "2026-08-01"
    })

    # 1. Daily Analytics
    daily_res = client.get("/api/v1/analytics/daily?date=2026-08-01")
    assert daily_res.status_code == 200
    assert float(daily_res.json()["total_amount"]) == 12000.0
    assert daily_res.json()["expense_count"] == 1

    # 2. Monthly Analytics
    monthly_res = client.get("/api/v1/analytics/monthly?month=8&year=2026")
    assert monthly_res.status_code == 200
    assert float(monthly_res.json()["total_amount"]) == 12000.0
    assert len(monthly_res.json()["daily_breakdown"]) == 31
    assert float(monthly_res.json()["daily_breakdown"][0]["amount"]) == 12000.0

    # 3. Yearly Analytics
    yearly_res = client.get("/api/v1/analytics/yearly?year=2026")
    assert yearly_res.status_code == 200
    assert float(yearly_res.json()["total_amount"]) == 12000.0
    assert len(yearly_res.json()["monthly_breakdown"]) == 1

    # 4. Category Analytics
    cat_res = client.get("/api/v1/analytics/categories?month=8&year=2026")
    assert cat_res.status_code == 200
    assert cat_res.json()[0]["category_name"] == "Rent"
    assert cat_res.json()[0]["percentage"] == 100.0
