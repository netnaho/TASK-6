from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_JWT_SECRET = "replace-me-with-long-secret-key"
DEFAULT_CAPTCHA_SECRET = "replace-me-captcha-secret"
DEFAULT_ENCRYPTION_KEY = "j8nQ3W-c_0LxgVe2B1u2Vt1n2HzAit5mfS_qwXcqfaQ="
SAFE_DEFAULT_ENVIRONMENTS = {"development", "dev", "test"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = "NutriDeclare Offline Compliance System"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    postgres_server: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "nutrideclare"
    postgres_password: str = "nutrideclare"
    postgres_db: str = "nutrideclare"
    database_url: str | None = None

    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_refresh_secret_key: str = "replace-me-refresh-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    refresh_token_pepper: str = "replace-me-refresh-pepper"

    password_history_count: int = 5
    lockout_failed_attempts: int = 5
    lockout_minutes: int = 15

    encryption_key: str = Field(
        default=DEFAULT_ENCRYPTION_KEY,
        description="URL-safe base64 encoded 32-byte key",
    )
    db_encryption_enabled: bool = True
    db_encryption_key: str | None = None

    enable_local_captcha: bool = True
    captcha_secret: str = DEFAULT_CAPTCHA_SECRET
    captcha_expire_minutes: int = 10

    storage_root: str = "/var/lib/nutrideclare/storage"
    export_mask: str = "***MASKED***"
    default_download_expiry_hours: int = 72
    notifications_retention_days: int = 90
    review_due_hours: int = 72
    audit_retention_years: int = 7
    audit_archive_enabled: bool = True
    audit_archive_format: str = "jsonl"

    cors_origins: list[str] = ["http://localhost:4173", "http://frontend:4173"]

    seed_participant_username: str = "participant_demo"
    seed_participant_password: str = "Participant#2026"
    seed_reviewer_username: str = "reviewer_demo"
    seed_reviewer_password: str = "Reviewer#2026"
    seed_admin_username: str = "admin_demo"
    seed_admin_password: str = "Admin#2026Secure"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_root)

    @property
    def effective_db_encryption_key(self) -> str:
        return self.db_encryption_key or self.encryption_key

    @model_validator(mode="after")
    def validate_runtime_secrets(self):
        if self.environment.lower() in SAFE_DEFAULT_ENVIRONMENTS:
            return self

        invalid = []
        if self.jwt_secret_key == DEFAULT_JWT_SECRET:
            invalid.append("JWT_SECRET_KEY")
        if self.captcha_secret == DEFAULT_CAPTCHA_SECRET:
            invalid.append("CAPTCHA_SECRET")
        if self.encryption_key == DEFAULT_ENCRYPTION_KEY:
            invalid.append("ENCRYPTION_KEY")

        if invalid:
            joined = ", ".join(invalid)
            raise RuntimeError(
                f"Refusing to start with default cryptographic material in {self.environment} mode. "
                f"Set real secrets via environment variables for: {joined}."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
