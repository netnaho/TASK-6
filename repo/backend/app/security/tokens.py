import hashlib
import secrets
from typing import Any

from jose import jwt

from app.core.config import get_settings
from app.utils.datetime import add_days, add_minutes, utc_now


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    payload = {"sub": subject, "type": "access", "exp": add_minutes(settings.access_token_expire_minutes)}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def create_refresh_token(subject: str) -> tuple[str, str, Any]:
    settings = get_settings()
    raw_token = secrets.token_urlsafe(48)
    db_expires_at = add_days(settings.refresh_token_expire_days)
    payload = {"sub": subject, "jti": raw_token, "type": "refresh", "exp": add_days(settings.refresh_token_expire_days)}
    encoded = jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)
    return encoded, hash_refresh_token(encoded), db_expires_at


def decode_refresh_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_refresh_secret_key, algorithms=[settings.jwt_algorithm])


def hash_refresh_token(token: str) -> str:
    settings = get_settings()
    return hashlib.sha256(f"{settings.refresh_token_pepper}:{token}".encode()).hexdigest()


def generate_download_token() -> str:
    return secrets.token_urlsafe(48)


def hash_download_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def compute_audit_hash(previous_hash: str | None, payload: dict[str, Any]) -> str:
    raw = f"{previous_hash or ''}:{payload}".encode()
    return hashlib.sha256(raw).hexdigest()
