import pytest


def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"
    assert "refresh_token" in response.cookies


def test_register_duplicate_email(client, auth_user_a):
    response = client.post("/api/v1/auth/register", json={
        "email": "user_a@example.com",
        "password": "AnotherPassword123!",
        "full_name": "Duplicate"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "EMAIL_ALREADY_EXISTS"


def test_login_success(client, auth_user_a):
    response = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "user_a@example.com"
    assert "refresh_token" in response.cookies


def test_login_invalid_password(client, auth_user_a):
    response = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_get_me(client, auth_user_a):
    # Valid auth header
    response = client.get("/api/v1/auth/me", headers=auth_user_a["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user_a@example.com"

    # Missing auth header -> 401
    unauth_resp = client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401


def test_change_password(client, auth_user_a):
    # Change password
    resp = client.post("/api/v1/auth/change-password", headers=auth_user_a["headers"], json={
        "old_password": "Password123!",
        "new_password": "NewSecretPassword999!"
    })
    assert resp.status_code == 200

    # Old password no longer works
    old_login = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "Password123!"
    })
    assert old_login.status_code == 401

    # New password works
    new_login = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "NewSecretPassword999!"
    })
    assert new_login.status_code == 200


def test_password_reset_flow(client, auth_user_a):
    # 1. Request reset
    forgot_resp = client.post("/api/v1/auth/forgot-password", json={
        "email": "user_a@example.com"
    })
    assert forgot_resp.status_code == 200
    data = forgot_resp.json()
    reset_token = data.get("reset_token")
    assert reset_token is not None

    # 2. Reset with token
    reset_resp = client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": "RecoveredPassword888!"
    })
    assert reset_resp.status_code == 200

    # 3. Login with recovered password
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "RecoveredPassword888!"
    })
    assert login_resp.status_code == 200
