import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import httpx
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.config import settings
from ..core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_random_token,
    hash_token,
)
from ..core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ResourceNotFoundException,
)
from ..models.user import User
from ..models.refresh_token import RefreshToken
from ..models.password_reset_token import PasswordResetToken
from ..schemas.auth import (
    UserRegister,
    UserLogin,
    UserProfileUpdate,
)

logger = logging.getLogger("app.services.auth")


def _is_expired(expires_at: datetime) -> bool:
    """Helper to safely check expiration across PostgreSQL (aware) and SQLite (naive) datetimes."""
    if expires_at.tzinfo is None:
        return expires_at < datetime.now(timezone.utc).replace(tzinfo=None)
    return expires_at < datetime.now(timezone.utc)


def register_user(
    db: Session,
    schema: UserRegister,
    request: Optional[Request] = None
) -> Tuple[User, str, str]:
    """Register a new user, create initial session, and return (user, access_token, raw_refresh_token)."""
    cleaned_email = schema.email.strip().lower()
    existing_user = db.query(User).filter(func.lower(User.email) == cleaned_email).first()
    if existing_user:
        raise BadRequestException(
            detail="An account with this email already exists",
            error_code="EMAIL_ALREADY_EXISTS"
        )

    user = User(
        email=cleaned_email,
        hashed_password=get_password_hash(schema.password),
        full_name=schema.full_name.strip() if schema.full_name else None,
        is_verified=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, raw_refresh_token = create_user_session(db, user, request)
    return user, access_token, raw_refresh_token


def authenticate_user(
    db: Session,
    schema: UserLogin,
    request: Optional[Request] = None
) -> Tuple[User, str, str]:
    """Authenticate an existing user with email and password."""
    cleaned_email = schema.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == cleaned_email).first()
    if not user or not verify_password(schema.password, user.hashed_password):
        raise UnauthorizedException(
            detail="Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )

    if not user.is_active:
        raise UnauthorizedException(
            detail="User account is deactivated",
            error_code="USER_INACTIVE"
        )

    access_token, raw_refresh_token = create_user_session(db, user, request)
    return user, access_token, raw_refresh_token


def authenticate_google(
    db: Session,
    credential: str,
    request: Optional[Request] = None
) -> Tuple[User, str, str]:
    """
    Validate Google ID Token / OpenID Connect credential server-side via Google's tokeninfo endpoint.
    Handles existing user account linking or creates a new user.
    """
    # 1. Verify token with Google
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}")
            if resp.status_code != 200:
                logger.warning(f"Google tokeninfo rejected token: {resp.text}")
                raise BadRequestException(
                    detail="Invalid or expired Google credential",
                    error_code="INVALID_GOOGLE_TOKEN"
                )
            payload = resp.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Google OAuth service: {e}")
        raise BadRequestException(
            detail="Unable to verify Google credential with authentication provider",
            error_code="AUTH_PROVIDER_UNAVAILABLE"
        )

    google_id = payload.get("sub")
    email = payload.get("email")
    email_verified = payload.get("email_verified")

    if not google_id or not email:
        raise BadRequestException(
            detail="Google account missing verified identity or email",
            error_code="INVALID_GOOGLE_TOKEN"
        )

    expected_client_id = settings.GOOGLE_CLIENT_ID.strip().strip('"').strip("'") if settings.GOOGLE_CLIENT_ID else None
    token_aud = payload.get("aud", "").strip() if payload.get("aud") else None

    if expected_client_id and token_aud and token_aud != expected_client_id:
        logger.warning(f"Google token audience mismatch: expected '{expected_client_id}', got '{token_aud}'")
        raise BadRequestException(
            detail="Google token audience mismatch",
            error_code="INVALID_GOOGLE_TOKEN"
        )

    if str(email_verified).lower() not in ("true", "1"):
        raise BadRequestException(
            detail="Google email must be verified to sign in",
            error_code="UNVERIFIED_EMAIL"
        )

    cleaned_email = email.strip().lower()
    full_name = payload.get("name")
    picture = payload.get("picture")

    # 2. Find user by google_id or email
    user = db.query(User).filter(
        (User.google_id == google_id) | (func.lower(User.email) == cleaned_email)
    ).first()

    is_new_user = False
    if user:
        # Link account if not already linked
        if not user.google_id:
            user.google_id = google_id
        if not user.avatar_url and picture:
            user.avatar_url = picture
        if not user.full_name and full_name:
            user.full_name = full_name
        user.is_verified = True
        db.commit()
        db.refresh(user)
    else:
        # Create new user via Google
        is_new_user = True
        user = User(
            email=cleaned_email,
            google_id=google_id,
            full_name=full_name,
            avatar_url=picture,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise UnauthorizedException(
            detail="User account is deactivated",
            error_code="USER_INACTIVE"
        )

    access_token, raw_refresh_token = create_user_session(db, user, request)
    return user, access_token, raw_refresh_token, is_new_user


def create_user_session(
    db: Session,
    user: User,
    request: Optional[Request] = None
) -> Tuple[str, str]:
    """Generate access token and persist a hashed refresh token for the user."""
    access_token = create_access_token(user.id, user.email)
    raw_refresh_token, token_hash = generate_random_token(64)

    device_info = None
    ip_address = None
    if request:
        device_info = request.headers.get("user-agent", "")[:250] if request.headers.get("user-agent") else None
        ip_address = request.client.host if request.client else None

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    session_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        device_info=device_info,
        ip_address=ip_address,
        is_revoked=False,
        expires_at=expires_at,
    )
    db.add(session_record)
    db.commit()

    return access_token, raw_refresh_token


def rotate_refresh_token(
    db: Session,
    raw_token: str,
    request: Optional[Request] = None
) -> Tuple[User, str, str]:
    """
    Validate and rotate refresh token.
    Enforces Refresh Token Rotation (RTR) and Token Reuse Detection.
    """
    token_hash = hash_token(raw_token)
    session_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not session_record:
        raise UnauthorizedException(
            detail="Invalid refresh token",
            error_code="INVALID_REFRESH_TOKEN"
        )

    user = session_record.user
    if not user or not user.is_active:
        raise UnauthorizedException(
            detail="User account is inactive or deleted",
            error_code="USER_INACTIVE"
        )

    # TOKEN REUSE DETECTION
    if session_record.is_revoked:
        logger.warning(
            f"Security Alert: Revoked refresh token reused for user ID {user.id}. Invalidating all user sessions."
        )
        revoke_all_user_sessions(db, user.id)
        raise UnauthorizedException(
            detail="Token reuse detected. All active sessions have been revoked for your security.",
            error_code="TOKEN_REUSE_DETECTED"
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    if _is_expired(session_record.expires_at):
        session_record.is_revoked = True
        session_record.revoked_at = now
        db.commit()
        raise UnauthorizedException(
            detail="Refresh token has expired. Please log in again.",
            error_code="TOKEN_EXPIRED"
        )

    # Mark current token revoked as part of rotation
    session_record.is_revoked = True
    session_record.revoked_at = now

    # Issue new token pair
    new_access_token = create_access_token(user.id, user.email)
    new_raw_refresh_token, new_token_hash = generate_random_token(64)

    device_info = session_record.device_info
    ip_address = session_record.ip_address
    if request:
        device_info = request.headers.get("user-agent", "")[:250] or device_info
        ip_address = request.client.host if request.client else ip_address

    new_session_record = RefreshToken(
        user_id=user.id,
        token_hash=new_token_hash,
        device_info=device_info,
        ip_address=ip_address,
        is_revoked=False,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_session_record)
    db.commit()

    return user, new_access_token, new_raw_refresh_token


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    """Revoke a single refresh token on logout."""
    token_hash = hash_token(raw_token)
    session_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if session_record and not session_record.is_revoked:
        session_record.is_revoked = True
        session_record.revoked_at = datetime.now(timezone.utc)
        db.commit()


def revoke_all_user_sessions(db: Session, user_id: int) -> None:
    """Revoke all active refresh tokens for a given user across all devices."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update(
        {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)},
        synchronize_session=False
    )
    db.commit()


def request_password_reset(db: Session, email: str) -> Optional[str]:
    """
    Generate single-use password reset token with 1-hour expiry.
    Returns raw token if user exists, else None.
    """
    cleaned_email = email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == cleaned_email).first()
    if not user:
        return None

    raw_token, token_hash = generate_random_token(48)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        used=False,
        expires_at=expires_at,
    )
    db.add(reset_record)
    db.commit()

    return raw_token


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    """Validate password reset token, update password hash, and revoke all active sessions."""
    token_hash = hash_token(raw_token)
    reset_record = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()

    now = datetime.now(timezone.utc)
    if not reset_record or reset_record.used or _is_expired(reset_record.expires_at):
        raise BadRequestException(
            detail="Password reset link is invalid or has expired",
            error_code="INVALID_RESET_TOKEN"
        )

    user = reset_record.user
    if not user:
        raise ResourceNotFoundException(detail="User not found", error_code="USER_NOT_FOUND")

    # Update password
    user.hashed_password = get_password_hash(new_password)
    reset_record.used = True

    # Revoke all sessions for security
    revoke_all_user_sessions(db, user.id)
    db.commit()


def change_password(
    db: Session,
    user: User,
    old_password: str,
    new_password: str
) -> None:
    """Change password for an authenticated user and revoke other active sessions."""
    if not verify_password(old_password, user.hashed_password):
        raise BadRequestException(
            detail="Current password is incorrect",
            error_code="INVALID_PASSWORD"
        )

    user.hashed_password = get_password_hash(new_password)
    revoke_all_user_sessions(db, user.id)
    db.commit()


def update_user_profile(
    db: Session,
    user: User,
    schema: UserProfileUpdate
) -> User:
    """Update user's name and avatar."""
    if schema.full_name is not None:
        user.full_name = schema.full_name.strip() if schema.full_name else None
    if schema.avatar_url is not None:
        user.avatar_url = schema.avatar_url.strip() if schema.avatar_url else None

    db.commit()
    db.refresh(user)
    return user
