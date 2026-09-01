import pytest
from app.core.security import create_access_token
from datetime import timedelta


def test_refresh_token_rotation(client):
    # 1. Register user
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "tokenuser@example.com",
        "password": "TokenPassword123!"
    })
    assert reg_resp.status_code == 201
    old_cookie = client.cookies.get("refresh_token")
    assert old_cookie is not None

    # 2. Call /refresh
    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    new_cookie = client.cookies.get("refresh_token")
    assert new_cookie is not None
    assert new_cookie != old_cookie


def test_token_reuse_detection(client):
    # 1. Register user
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "reuseuser@example.com",
        "password": "ReusePassword123!"
    })
    assert reg_resp.status_code == 201
    stolen_token = client.cookies.get("refresh_token")

    # 2. Legitimate user rotates token
    legit_refresh = client.post("/api/v1/auth/refresh")
    assert legit_refresh.status_code == 200

    # 3. Attacker presents old/rotated token -> Should trigger reuse detection!
    client.cookies.set("refresh_token", stolen_token)
    attacker_resp = client.post("/api/v1/auth/refresh")
    assert attacker_resp.status_code == 401
    assert attacker_resp.json()["error_code"] == "TOKEN_REUSE_DETECTED"

    # 4. Now all user sessions are invalidated; legitimate user also needs to re-authenticate
    legit_next_refresh = client.post("/api/v1/auth/refresh")
    assert legit_next_refresh.status_code == 401


def test_logout_revokes_token(client):
    # 1. Register & Login
    client.post("/api/v1/auth/register", json={
        "email": "logoutuser@example.com",
        "password": "LogoutPassword123!"
    })
    assert "refresh_token" in client.cookies

    # 2. Logout
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 204

    # 3. Subsequent refresh fails
    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 401


def test_logout_all_devices(client, auth_user_a):
    # User A calls logout-all
    logout_all_resp = client.post("/api/v1/auth/logout-all", headers=auth_user_a["headers"])
    assert logout_all_resp.status_code == 200
    assert logout_all_resp.json()["status"] == "all_sessions_revoked"

    # Refresh token fails
    refresh_resp = client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 401


def test_expired_or_invalid_jwt(client):
    # Forged JWT
    forged_headers = {"Authorization": "Bearer invalid.jwt.token"}
    resp = client.get("/api/v1/auth/me", headers=forged_headers)
    assert resp.status_code == 401

    # Expired token
    expired_token = create_access_token(user_id=1, email="expired@example.com", expires_delta=timedelta(seconds=-10))
    expired_headers = {"Authorization": f"Bearer {expired_token}"}
    resp2 = client.get("/api/v1/auth/me", headers=expired_headers)
    assert resp2.status_code == 401
