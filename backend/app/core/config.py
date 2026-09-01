from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ExpenseFlow"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/expenseflow"
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000"]
    SEED_ON_STARTUP: bool = True
    LOG_LEVEL: str = "INFO"

    # JWT & Auth Settings (Environment-driven)
    JWT_SECRET_KEY: str = "expenseflow_super_secret_jwt_key_change_in_production_2026_x9k2"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60

    # Cookie Settings
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Union[str, None] = None

    # Google OAuth 2.0 Settings
    GOOGLE_CLIENT_ID: Union[str, None] = None
    GOOGLE_CLIENT_SECRET: Union[str, None] = None

    # Frontend URL for password reset links & redirects
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
