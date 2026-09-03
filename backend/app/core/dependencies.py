import time
from collections import defaultdict
from typing import Optional, Dict, List, Callable
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .security import decode_access_token
from .exceptions import UnauthorizedException, RateLimitException
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract, validate JWT access token and retrieve current authenticated user.
    Raises UnauthorizedException on missing, expired, or invalid token.
    """
    if not token:
        raise UnauthorizedException(
            detail="Authentication credentials were not provided",
            error_code="NOT_AUTHENTICATED"
        )

    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException(
            detail="Invalid or expired access token",
            error_code="INVALID_TOKEN"
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(
            detail="Token payload is missing subject claim",
            error_code="INVALID_TOKEN"
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedException(
            detail="Invalid user identifier in token",
            error_code="INVALID_TOKEN"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException(
            detail="User not found",
            error_code="USER_NOT_FOUND"
        )

    if not user.is_active:
        raise UnauthorizedException(
            detail="User account is deactivated",
            error_code="USER_INACTIVE"
        )

    return user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Retrieve current user if valid token is provided, otherwise return None."""
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except UnauthorizedException:
        return None


# Lightweight in-memory sliding window rate limiter
_request_history: Dict[str, List[float]] = defaultdict(list)


def rate_limit(
    key_prefix: str,
    max_requests: int = 10,
    window_seconds: int = 60
) -> Callable[[Request], bool]:
    """
    Rate limiting dependency function.
    Tracks client IP within sliding window of window_seconds.
    Bypassed during automated tests.
    """
    def limiter(request: Request):
        if settings.APP_ENV in ("test", "testing"):
            return True

        client_ip = request.client.host if request.client else "unknown"
        if client_ip in ("testclient", "127.0.0.1", "localhost") and settings.APP_ENV != "production":
            return True

        key = f"{key_prefix}:{client_ip}"
        now = time.time()
        window_start = now - window_seconds

        # Clean old timestamps
        timestamps = [ts for ts in _request_history[key] if ts > window_start]
        if len(timestamps) >= max_requests:
            raise RateLimitException(
                detail="Too many attempts. Please try again in a minute.",
                error_code="RATE_LIMIT_EXCEEDED"
            )

        timestamps.append(now)
        _request_history[key] = timestamps
        return True

    return limiter
