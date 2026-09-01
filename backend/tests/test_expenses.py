def test_expense_crud_and_search(client, auth_user_a):
    headers = auth_user_a["headers"]
    cats = client.get("/api/v1/categories", headers=headers).json()
    cat_id = cats[0]["id"]

    # 1. Create expense
    res = client.post("/api/v1/expenses", headers=headers, json={
        "amount": 1200.50,
        "category_id": cat_id,
        "description": "Grocery shopping",
        "notes": "Bought vegetables and fruits",
        "date": "2026-08-25",
        "payment_method": "Credit Card"
    })
    assert res.status_code == 201
    exp_id = res.json()["id"]

    # 2. Get expense by ID
    get_res = client.get(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["description"] == "Grocery shopping"

    # 3. Update expense
    put_res = client.put(f"/api/v1/expenses/{exp_id}", headers=headers, json={
        "description": "Updated Grocery Shopping",
        "amount": 1300.00
    })
    assert put_res.status_code == 200
    assert put_res.json()["description"] == "Updated Grocery Shopping"
    assert float(put_res.json()["amount"]) == 1300.00

    # 4. Search expenses
    search_res = client.get("/api/v1/expenses?search=Grocery", headers=headers)
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1
    assert search_res.json()["items"][0]["id"] == exp_id

    # 5. Filter expenses by date range
    date_res = client.get("/api/v1/expenses?date_from=2026-08-01&date_to=2026-08-31", headers=headers)
    assert date_res.status_code == 200
    assert date_res.json()["total"] == 1

    # 6. Export expenses as CSV
    export_csv = client.get("/api/v1/expenses/export?format=csv", headers=headers)
    assert export_csv.status_code == 200
    assert "text/csv" in export_csv.headers["content-type"]
    assert "Updated Grocery Shopping" in export_csv.text

    # 7. Export expenses as PDF
    export_pdf = client.get("/api/v1/expenses/export?format=pdf", headers=headers)
    assert export_pdf.status_code == 200
    assert "application/pdf" in export_pdf.headers["content-type"]
    assert len(export_pdf.content) > 100

    # 8. Delete expense
    del_res = client.delete(f"/api/v1/expenses/{exp_id}", headers=headers)
    assert del_res.status_code == 204


def test_expense_error_cases(client, auth_user_a):
    headers = auth_user_a["headers"]

    # Invalid category ID
    res_inv_cat = client.post("/api/v1/expenses", headers=headers, json={
        "amount": 100.0,
        "category_id": 99999,
        "description": "Invalid",
        "date": "2026-08-27"
    })
    assert res_inv_cat.status_code == 400
    assert res_inv_cat.json()["error_code"] == "INVALID_CATEGORY"

    # Non-existent expense 404
    res_404 = client.get("/api/v1/expenses/99999", headers=headers)
    assert res_404.status_code == 404
    assert res_404.json()["error_code"] == "EXPENSE_NOT_FOUND"

    # Invalid export format
    res_fmt = client.get("/api/v1/expenses/export?format=xml", headers=headers)
    assert res_fmt.status_code == 400
    assert res_fmt.json()["error_code"] == "UNSUPPORTED_FORMAT"
