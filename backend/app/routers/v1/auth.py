from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from ...core.config import settings
from ...core.database import get_db
from ...core.dependencies import get_current_user, rate_limit
from ...core.exceptions import UnauthorizedException
from ...models.user import User
from ...schemas.auth import (
    UserRegister,
    UserLogin,
    GoogleAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from ...services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & Session"])


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    """Helper to attach the secure HttpOnly refresh token cookie to the response."""
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    is_secure = settings.COOKIE_SECURE or (settings.APP_ENV == "production")
    
    # In production across different domains (vercel.app <-> onrender.com),
    # SameSite must be 'none' and Secure must be True for cross-site cookie transmission.
    # In local development over HTTP, SameSite is 'lax' and Secure is False.
    samesite = settings.COOKIE_SAMESITE
    if is_secure and samesite.lower() == "lax" and settings.APP_ENV == "production":
        samesite = "none"

    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        max_age=max_age,
        httponly=True,
        secure=is_secure,
        samesite=samesite,
        domain=settings.COOKIE_DOMAIN,
        path=f"{settings.API_V1_PREFIX}/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Helper to clear the refresh token cookie upon logout."""
    is_secure = settings.COOKIE_SECURE or (settings.APP_ENV == "production")
    samesite = settings.COOKIE_SAMESITE
    if is_secure and samesite.lower() == "lax" and settings.APP_ENV == "production":
        samesite = "none"

    response.delete_cookie(
        key="refresh_token",
        path=f"{settings.API_V1_PREFIX}/auth",
        domain=settings.COOKIE_DOMAIN,
        httponly=True,
        secure=is_secure,
        samesite=samesite,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    schema: UserRegister,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _limit=Depends(rate_limit("auth:register", max_requests=10, window_seconds=60)),
):
    """Register a new user, issue in-memory access token and HttpOnly refresh token cookie."""
    user, access_token, raw_refresh_token = auth_service.register_user(db, schema, request)
    _set_refresh_cookie(response, raw_refresh_token)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    schema: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _limit=Depends(rate_limit("auth:login", max_requests=15, window_seconds=60)),
):
    """Authenticate with email and password, issuing access token and HttpOnly refresh cookie."""
    user, access_token, raw_refresh_token = auth_service.authenticate_user(db, schema, request)
    _set_refresh_cookie(response, raw_refresh_token)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/google", response_model=TokenResponse)
def google_sign_in(
    schema: GoogleAuthRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Authenticate or register user using Google OAuth 2.0 / OpenID Connect ID token."""
    user, access_token, raw_refresh_token = auth_service.authenticate_google(db, schema.credential, request)
    _set_refresh_cookie(response, raw_refresh_token)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Exchange an existing valid refresh token for a new access token + rotated refresh token.
    Reads token from HttpOnly cookie, with request body fallback.
    """
    raw_token = request.cookies.get("refresh_token")
    if not raw_token and body and body.refresh_token:
        raw_token = body.refresh_token

    if not raw_token:
        raise UnauthorizedException(
            detail="Refresh token is required",
            error_code="MISSING_REFRESH_TOKEN"
        )

    user, new_access_token, new_raw_refresh_token = auth_service.rotate_refresh_token(
        db, raw_token, request
    )
    _set_refresh_cookie(response, new_raw_refresh_token)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db),
):
    """Revoke the current session refresh token and delete the HttpOnly cookie."""
    raw_token = request.cookies.get("refresh_token")
    if not raw_token and body and body.refresh_token:
        raw_token = body.refresh_token

    if raw_token:
        auth_service.revoke_refresh_token(db, raw_token)

    _clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout-all")
def logout_all_devices(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke all active sessions for the current user across all devices."""
    auth_service.revoke_all_user_sessions(db, current_user.id)
    _clear_refresh_cookie(response)
    return {"status": "all_sessions_revoked", "message": "Logged out from all active devices"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile of currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    schema: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile details (name, avatar) for current user."""
    updated_user = auth_service.update_user_profile(db, current_user, schema)
    return UserResponse.model_validate(updated_user)


@router.post("/change-password")
def change_password(
    schema: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password for authenticated user and invalidate other active sessions."""
    auth_service.change_password(db, current_user, schema.old_password, schema.new_password)
    return {"status": "password_updated", "message": "Password changed successfully"}


@router.post("/forgot-password")
def forgot_password(
    schema: PasswordResetRequest,
    db: Session = Depends(get_db),
    _limit=Depends(rate_limit("auth:forgot_pwd", max_requests=5, window_seconds=60)),
):
    """Generate a password reset token for account recovery."""
    raw_token = auth_service.request_password_reset(db, schema.email)
    # In production, this would send an email with the link `${settings.FRONTEND_URL}/reset-password?token=${raw_token}`
    return {
        "status": "success",
        "message": "If that email is registered in ExpenseFlow, a password reset link has been created.",
        "reset_token": raw_token if settings.APP_ENV != "production" else None,
    }


@router.post("/reset-password")
def reset_password(
    schema: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """Reset password using a valid reset token and revoke all active sessions."""
    auth_service.reset_password(db, schema.token, schema.new_password)
    return {
        "status": "password_reset_success",
        "message": "Password has been reset successfully. You may now log in with your new password."
    }
