def test_get_categories_seeded(client, auth_user_a):
    headers = auth_user_a["headers"]
    response = client.get("/api/v1/categories", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    cat_names = [c["name"] for c in data]
    assert "Food" in cat_names
    assert "Transport" in cat_names


def test_create_category(client, auth_user_a):
    headers = auth_user_a["headers"]
    response = client.post("/api/v1/categories", headers=headers, json={"name": "Subscriptions"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Subscriptions"
    assert "id" in data


def test_create_duplicate_category_fails(client, auth_user_a):
    headers = auth_user_a["headers"]
    client.post("/api/v1/categories", headers=headers, json={"name": "Gym"})
    response = client.post("/api/v1/categories", headers=headers, json={"name": "Gym"})
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "CATEGORY_ALREADY_EXISTS"


def test_delete_category_in_use_protection(client, auth_user_a):
    headers = auth_user_a["headers"]
    # Create custom categories for user
    c1 = client.post("/api/v1/categories", headers=headers, json={"name": "Custom Dining"}).json()
    c2 = client.post("/api/v1/categories", headers=headers, json={"name": "Custom Travel"}).json()

    # Create expense under Custom Dining
    exp_res = client.post("/api/v1/expenses", headers=headers, json={
        "amount": 250.0,
        "category_id": c1["id"],
        "description": "Lunch",
        "date": "2026-08-27"
    })
    assert exp_res.status_code == 201

    # Attempt to delete Custom Dining category without reassign_to should fail
    del_res = client.delete(f"/api/v1/categories/{c1['id']}", headers=headers)
    assert del_res.status_code == 400
    assert del_res.json()["error_code"] == "CATEGORY_IN_USE"

    # Delete Custom Dining category with reassign_to Custom Travel should succeed
    del_reassign_res = client.delete(f"/api/v1/categories/{c1['id']}?reassign_to={c2['id']}", headers=headers)
    assert del_reassign_res.status_code == 204
