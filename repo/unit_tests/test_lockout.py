import pytest

from app.core.exceptions import AuthenticationError
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def test_lockout_after_five_failed_attempts(db_session):
    service = AuthService(db_session)
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            service.login("participant_demo", "wrong-password")
    user = UserRepository(db_session).get_by_username("participant_demo")
    assert user.locked_until is not None
    with pytest.raises(AuthenticationError, match="locked"):
        service.login("participant_demo", "Participant#2026")
