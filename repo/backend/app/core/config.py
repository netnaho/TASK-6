import base64
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_POSTGRES_PASSWORD = "replace-me-postgres-password"
DEFAULT_JWT_SECRET = "replace-me-with-long-secret-key"
DEFAULT_JWT_REFRESH_SECRET = "replace-me-refresh-secret-key"
DEFAULT_REFRESH_TOKEN_PEPPER = "replace-me-refresh-pepper"
DEFAULT_CAPTCHA_SECRET = "replace-me-captcha-secret"
DEFAULT_ENCRYPTION_KEY = "j8nQ3W-c_0LxgVe2B1u2Vt1n2HzAit5mfS_qwXcqfaQ="
DEFAULT_SEED_PARTICIPANT_PASSWORD = "replace-me-participant-password"
DEFAULT_SEED_REVIEWER_PASSWORD = "replace-me-reviewer-password"
DEFAULT_SEED_ADMIN_PASSWORD = "replace-me-admin-password"


def _is_placeholder_secret(value: str, placeholder: str, *, min_length: int = 32) -> bool:
    return not value or value == placeholder or len(value.strip()) < min_length


def _is_valid_encryption_key(value: str) -> bool:
    try:
        return len(base64.urlsafe_b64decode(value.encode())) == 32
    except Exception:
        return False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_name: str = "NutriDeclare Offline Compliance System"
    environment: str = "development"
    testing: bool = False
    allow_insecure_dev_mode: bool = False
    seed_demo_data: bool = False
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    postgres_server: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "nutrideclare"
    postgres_password: str = DEFAULT_POSTGRES_PASSWORD
    postgres_db: str = "nutrideclare"
    database_url: str | None = None

    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_refresh_secret_key: str = DEFAULT_JWT_REFRESH_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    refresh_token_pepper: str = DEFAULT_REFRESH_TOKEN_PEPPER

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
    seed_participant_password: str = DEFAULT_SEED_PARTICIPANT_PASSWORD
    seed_reviewer_username: str = "reviewer_demo"
    seed_reviewer_password: str = DEFAULT_SEED_REVIEWER_PASSWORD
    seed_admin_username: str = "admin_demo"
    seed_admin_password: str = DEFAULT_SEED_ADMIN_PASSWORD

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
        if self.testing or self.allow_insecure_dev_mode:
            return self

        invalid = []
        if _is_placeholder_secret(self.jwt_secret_key, DEFAULT_JWT_SECRET):
            invalid.append("JWT_SECRET_KEY")
        if _is_placeholder_secret(self.jwt_refresh_secret_key, DEFAULT_JWT_REFRESH_SECRET):
            invalid.append("JWT_REFRESH_SECRET_KEY")
        if _is_placeholder_secret(self.refresh_token_pepper, DEFAULT_REFRESH_TOKEN_PEPPER):
            invalid.append("REFRESH_TOKEN_PEPPER")
        if self.postgres_password == DEFAULT_POSTGRES_PASSWORD:
            invalid.append("POSTGRES_PASSWORD")
        if self.enable_local_captcha and _is_placeholder_secret(self.captcha_secret, DEFAULT_CAPTCHA_SECRET):
            invalid.append("CAPTCHA_SECRET")
        if self.encryption_key == DEFAULT_ENCRYPTION_KEY or not _is_valid_encryption_key(self.encryption_key):
            invalid.append("ENCRYPTION_KEY")
        if self.db_encryption_key is not None and len(self.db_encryption_key.strip()) < 32:
            invalid.append("DB_ENCRYPTION_KEY")

        if invalid:
            joined = ", ".join(invalid)
            raise RuntimeError(
                "Refusing to start without strong runtime secrets. "
                f"Set real values via environment variables for: {joined}. "
                "Use TESTING=true for automated tests or ALLOW_INSECURE_DEV_MODE=true only for disposable local demos."
            )

        if self.seed_demo_data:
            demo_invalid = []
            if self.seed_participant_password == DEFAULT_SEED_PARTICIPANT_PASSWORD:
                demo_invalid.append("SEED_PARTICIPANT_PASSWORD")
            if self.seed_reviewer_password == DEFAULT_SEED_REVIEWER_PASSWORD:
                demo_invalid.append("SEED_REVIEWER_PASSWORD")
            if self.seed_admin_password == DEFAULT_SEED_ADMIN_PASSWORD:
                demo_invalid.append("SEED_ADMIN_PASSWORD")
            if demo_invalid:
                joined = ", ".join(demo_invalid)
                raise RuntimeError(
                    "Refusing to seed demo users with placeholder credentials. "
                    f"Set strong values for: {joined}."
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
