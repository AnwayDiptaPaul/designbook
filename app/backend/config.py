# pyre-ignore-all-errors
"""Application settings loaded from the repository environment boundary."""

from pathlib import Path
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "DesignBook — RCC Structural Design"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://designbook:designbook@localhost:5432/designbook"

    # ── Redis / Celery ────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── JWT ───────────────────────────────────────────────
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Schema creation is a local bootstrap escape hatch only. Production uses
    # an explicit migration job once Alembic is bootstrapped.
    CREATE_SCHEMA_ON_STARTUP: bool = False
    # Explicit opt-in until the isolated worker and deployment dependencies are reviewed.
    ENABLE_ANALYSIS_EXECUTION: bool = False

    # ── File paths ────────────────────────────────────────
    DESIGN_EXCEL_DIR: str = "doc-files/design-excel"
    ENHANCED_EXCEL_DIR: str = "doc-files/design-excel/enhanced"
    REGULATIONS_DIR: str = "doc-files/regulations"

    # ── CORS ──────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=APP_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_environment_safety(self) -> "Settings":
        """Reject unsafe shared-environment defaults at application startup."""

        if self.ENVIRONMENT in {"staging", "production"}:
            if not self.SECRET_KEY or self.SECRET_KEY.startswith("change-me"):
                raise ValueError("SECRET_KEY must be explicitly configured outside local development")
            if self.DEBUG:
                raise ValueError("DEBUG must be false outside local development")
            if self.CREATE_SCHEMA_ON_STARTUP:
                raise ValueError("CREATE_SCHEMA_ON_STARTUP must be false outside local development")
        return self

    def resolve_path(self, configured_path: str) -> Path:
        """Resolve a configured reference path relative to the repository root."""

        path = Path(configured_path)
        return path if path.is_absolute() else (APP_ROOT.parent / path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
