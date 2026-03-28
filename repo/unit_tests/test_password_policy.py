import pytest

from app.core.exceptions import ValidationError
from app.security.passwords import validate_password_policy


def test_password_policy_accepts_strong_password():
    validate_password_policy("StrongPass#2026")


@pytest.mark.parametrize(
    "password",
    ["short", "alllowercasepassword", "NOLOWERCASE123", "ALLUPPER!!!!!"],
)
def test_password_policy_rejects_weak_passwords(password: str):
    with pytest.raises(ValidationError):
        validate_password_policy(password)
