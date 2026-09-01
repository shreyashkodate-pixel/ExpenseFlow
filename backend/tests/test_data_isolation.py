import pytest
from datetime import date


def test_expense_data_isolation(client, auth_user_a, auth_user_b):
    # 1. User A creates an expense
    create_resp = client.post(
        "/api/v1/expenses",
        headers=auth_user_a["headers"],
        json={
            "amount": 250.00,
            "category_id": 1,
            "description": "User A Private Dinner",
            "date": str(date.today()),
            "payment_method": "UPI"
        }
    )
    assert create_resp.status_code == 201
    expense_a_id = create_resp.json()["id"]

    # 2. User A can retrieve it
    get_a_resp = client.get(f"/api/v1/expenses/{expense_a_id}", headers=auth_user_a["headers"])
    assert get_a_resp.status_code == 200
    assert get_a_resp.json()["description"] == "User A Private Dinner"

    # 3. User B CANNOT see it by direct ID -> Returns 404 (zero information leakage)
    get_b_resp = client.get(f"/api/v1/expenses/{expense_a_id}", headers=auth_user_b["headers"])
    assert get_b_resp.status_code == 404

    # 4. User B CANNOT see it in list
    list_b_resp = client.get("/api/v1/expenses", headers=auth_user_b["headers"])
    assert list_b_resp.status_code == 200
    assert len(list_b_resp.json()["items"]) == 0
    assert list_b_resp.json()["total"] == 0

    # 5. User B CANNOT modify User A's expense
    put_b_resp = client.put(
        f"/api/v1/expenses/{expense_a_id}",
        headers=auth_user_b["headers"],
        json={"amount": 999.00}
    )
    assert put_b_resp.status_code == 404

    # 6. User B CANNOT delete User A's expense
    del_b_resp = client.delete(f"/api/v1/expenses/{expense_a_id}", headers=auth_user_b["headers"])
    assert del_b_resp.status_code == 404

    # 7. Verify expense is still intact for User A
    get_a_again = client.get(f"/api/v1/expenses/{expense_a_id}", headers=auth_user_a["headers"])
    assert get_a_again.status_code == 200
    assert float(get_a_again.json()["amount"]) == 250.00


def test_budget_data_isolation(client, auth_user_a, auth_user_b):
    # User A creates a budget
    budget_resp = client.post(
        "/api/v1/budgets",
        headers=auth_user_a["headers"],
        json={
            "month": 8,
            "year": 2026,
            "amount": 50000.00,
            "category_id": None
        }
    )
    assert budget_resp.status_code == 201
    budget_a_id = budget_resp.json()["id"]

    # User B list budgets -> Empty
    b_list_resp = client.get("/api/v1/budgets", headers=auth_user_b["headers"])
    assert b_list_resp.status_code == 200
    assert len(b_list_resp.json()) == 0

    # User B attempts to delete User A's budget -> 404
    b_del_resp = client.delete(f"/api/v1/budgets/{budget_a_id}", headers=auth_user_b["headers"])
    assert b_del_resp.status_code == 404


def test_analytics_and_dashboard_isolation(client, auth_user_a, auth_user_b):
    today_str = str(date.today())

    # User A logs ₹1000
    client.post(
        "/api/v1/expenses",
        headers=auth_user_a["headers"],
        json={"amount": 1000.00, "category_id": 1, "description": "Expense A", "date": today_str}
    )

    # User B logs ₹300
    client.post(
        "/api/v1/expenses",
        headers=auth_user_b["headers"],
        json={"amount": 300.00, "category_id": 1, "description": "Expense B", "date": today_str}
    )

    # User A Dashboard summary
    dash_a = client.get("/api/v1/dashboard", headers=auth_user_a["headers"]).json()
    assert float(dash_a["current_month_spending"]) == 1000.00
    assert dash_a["total_expense_count"] == 1

    # User B Dashboard summary
    dash_b = client.get("/api/v1/dashboard", headers=auth_user_b["headers"]).json()
    assert float(dash_b["current_month_spending"]) == 300.00
    assert dash_b["total_expense_count"] == 1
