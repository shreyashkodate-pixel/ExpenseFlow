def test_budget_creation_and_status(client, auth_user_a):
    headers = auth_user_a["headers"]
    cats = client.get("/api/v1/categories", headers=headers).json()
    food_cat_id = cats[0]["id"]

    # 1. Create overall monthly budget for August 2026
    overall_res = client.post("/api/v1/budgets", headers=headers, json={
        "month": 8,
        "year": 2026,
        "amount": 10000.0,
        "category_id": None
    })
    assert overall_res.status_code == 201
    assert float(overall_res.json()["amount"]) == 10000.00

    # 2. Add expense of 2500 in August 2026
    client.post("/api/v1/expenses", headers=headers, json={
        "amount": 2500.0,
        "category_id": food_cat_id,
        "description": "Dinner",
        "date": "2026-08-15"
    })

    # 3. Check budget status
    status_res = client.get("/api/v1/budgets/status?month=8&year=2026", headers=headers)
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["overall_budget"] is not None
    assert float(data["overall_budget"]["spent_amount"]) == 2500.0
    assert float(data["overall_budget"]["remaining_amount"]) == 7500.0
    assert data["overall_budget"]["percentage_used"] == 25.0
    assert data["overall_budget"]["status_level"] == "ok"
