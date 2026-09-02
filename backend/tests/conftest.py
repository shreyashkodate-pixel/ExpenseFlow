import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.seed.seed_data import seed_initial_categories

settings.APP_ENV = "testing"

# SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Create all tables (users, expenses, budgets, categories, refresh_tokens, password_reset_tokens)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    # Seed starter categories
    seed_initial_categories(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
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


@pytest.fixture
def auth_user_a(client, db_session):
    """Register and verify User A, returning dict with user, access_token, and auth headers."""
    from app.models.user import User
    from app.models.email_verification_token import EmailVerificationToken
    
    resp = client.post("/api/v1/auth/register", json={
        "email": "user_a@example.com",
        "password": "Password123!",
        "full_name": "Alice User"
    })
    assert resp.status_code == 201, resp.text

    # Manually mark as verified for fixture login
    user = db_session.query(User).filter(User.email == "user_a@example.com").first()
    user.is_verified = True
    db_session.commit()

    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user_a@example.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200, login_resp.text
    data = login_resp.json()
    token = data["access_token"]
    return {
        "user": data["user"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def auth_user_b(client, db_session):
    """Register and verify User B, returning dict with user, access_token, and auth headers."""
    from app.models.user import User

    resp = client.post("/api/v1/auth/register", json={
        "email": "user_b@example.com",
        "password": "Password456!",
        "full_name": "Bob User"
    })
    assert resp.status_code == 201, resp.text

    # Manually mark as verified for fixture login
    user = db_session.query(User).filter(User.email == "user_b@example.com").first()
    user.is_verified = True
    db_session.commit()

    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user_b@example.com",
        "password": "Password456!"
    })
    assert login_resp.status_code == 200, login_resp.text
    data = login_resp.json()
    token = data["access_token"]
    return {
        "user": data["user"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
