from argon2 import PasswordHasher

from app.core.config import get_settings
from app.core.exceptions import ValidationError


password_hasher = PasswordHasher()


def validate_password_policy(password: str) -> None:
    settings = get_settings()
    if len(password) < 12:
        raise ValidationError("Password must be at least 12 characters long.", field="password")

    classes = 0
    classes += any(c.isupper() for c in password)
    classes += any(c.islower() for c in password)
    classes += any(c.isdigit() for c in password)
    classes += any(not c.isalnum() for c in password)
    if classes < 3:
        raise ValidationError("Password must contain at least 3 of 4 character classes.", field="password")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except Exception:
        return False


def ensure_not_in_history(password: str, hashes: list[str]) -> None:
    settings = get_settings()
    for password_hash in hashes[: settings.password_history_count]:
        if verify_password(password, password_hash):
            raise ValidationError("New password cannot match any of the last 5 passwords.", field="password")
