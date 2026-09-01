import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
import bcrypt
import jwt
from .config import settings


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Verify a plaintext password against its BCrypt hash."""
    if not hashed_password or not plain_password:
        return False
    try:
        # Truncate to 72 bytes for BCrypt standard constraint
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate a secure BCrypt hash for a plaintext password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(
    user_id: int,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed, short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def hash_token(raw_token: str) -> str:
    """Compute SHA-256 hex digest of a token string for safe database storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_random_token(length: int = 64) -> Tuple[str, str]:
    """
    Generate a cryptographically secure random token string and its SHA-256 hash.
    Returns: (raw_token, token_hash)
    """
    raw_token = secrets.token_urlsafe(length)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash
