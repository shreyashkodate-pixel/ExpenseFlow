import pytest


def test_register_success(client, db_session):
    from app.models.email_verification_token import EmailVerificationToken
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "verification_pending"
    assert data["email"] == "newuser@example.com"
    assert "access_token" not in data

    # Verify token was created in database
    token_record = db_session.query(EmailVerificationToken).first()
    assert token_record is not None
    assert token_record.used is False


def test_login_unverified_user_fails(client):
    # Register unverified user
    client.post("/api/v1/auth/register", json={
        "email": "unverified@example.com",
        "password": "Password123!",
        "full_name": "Unverified User"
    })

    # Attempt login without verifying email
    response = client.post("/api/v1/auth/login", json={
        "email": "unverified@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 403
    assert response.json()["error_code"] == "EMAIL_NOT_VERIFIED"


def test_email_verification_flow(client, db_session):
    from app.services import auth_service
    # 1. Register user
    client.post("/api/v1/auth/register", json={
        "email": "verify_me@example.com",
        "password": "Password123!",
        "full_name": "Verify Me"
    })

    # Generate/retrieve token
    user, raw_token = auth_service.request_resend_verification(db_session, "verify_me@example.com")
    assert raw_token is not None

    # 2. Verify with token
    verify_resp = client.post("/api/v1/auth/verify-email", json={
        "token": raw_token
    })
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "access_token" in data
    assert data["user"]["is_verified"] is True
    assert "refresh_token" in verify_resp.cookies

    # 3. Login now succeeds
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "verify_me@example.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200


def test_resend_verification_endpoint(client):
    # Register user
    client.post("/api/v1/auth/register", json={
        "email": "resend_test@example.com",
        "password": "Password123!"
    })

    # Resend verification
    resend_resp = client.post("/api/v1/auth/resend-verification", json={
        "email": "resend_test@example.com"
    })
    assert resend_resp.status_code == 200
    assert resend_resp.json()["status"] == "success"



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


def test_password_reset_flow(client, auth_user_a, db_session):
    from app.services import auth_service
    # 1. Request reset for existing user -> 200 OK
    forgot_resp = client.post("/api/v1/auth/forgot-password", json={
        "email": "user_a@example.com"
    })
    assert forgot_resp.status_code == 200
    assert "sent" in forgot_resp.json()["message"].lower()

    # Generate token directly via auth_service for testing reset-password endpoint
    reset_token = auth_service.request_password_reset(db_session, "user_a@example.com")
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


def test_forgot_password_unregistered_email(client):
    resp = client.post("/api/v1/auth/forgot-password", json={
        "email": "nonexistent_dummy@example.com"
    })
    assert resp.status_code == 404
    assert resp.json()["error_code"] == "USER_NOT_FOUND"


def test_welcome_email_service():
    from app.services.email_service import send_welcome_email
    # Dev mode / unconfigured SMTP should succeed safely
    assert send_welcome_email("testwelcome@example.com", "Test User") is True
    assert send_welcome_email("testwelcome_noname@example.com", None) is True


def test_verification_email_service():
    from app.services.email_service import send_verification_email
    # Dev mode / unconfigured SMTP should succeed safely
    assert send_verification_email("testverify@example.com", "dummy_token_123", "Test User") is True
    assert send_verification_email("testverify_noname@example.com", "dummy_token_123", None) is True


