def test_get_categories_seeded(client):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    cat_names = [c["name"] for c in data]
    assert "Food" in cat_names
    assert "Transport" in cat_names


def test_create_category(client):
    response = client.post("/api/v1/categories", json={"name": "Subscriptions"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Subscriptions"
    assert "id" in data


def test_create_duplicate_category_fails(client):
    client.post("/api/v1/categories", json={"name": "Gym"})
    response = client.post("/api/v1/categories", json={"name": "Gym"})
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "CATEGORY_ALREADY_EXISTS"


def test_delete_category_in_use_protection(client):
    # Get Food category ID
    cats = client.get("/api/v1/categories").json()
    food_cat = next(c for c in cats if c["name"] == "Food")
    transport_cat = next(c for c in cats if c["name"] == "Transport")

    # Create expense under Food
    exp_res = client.post("/api/v1/expenses", json={
        "amount": 250.0,
        "category_id": food_cat["id"],
        "description": "Lunch",
        "date": "2026-08-27"
    })
    assert exp_res.status_code == 201

    # Attempt to delete Food category without reassign_to should fail
    del_res = client.delete(f"/api/v1/categories/{food_cat['id']}")
    assert del_res.status_code == 400
    assert del_res.json()["error_code"] == "CATEGORY_IN_USE"

    # Delete Food category with reassign_to Transport should succeed
    del_reassign_res = client.delete(f"/api/v1/categories/{food_cat['id']}?reassign_to={transport_cat['id']}")
    assert del_reassign_res.status_code == 204
