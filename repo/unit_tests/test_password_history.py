import pytest

from app.core.exceptions import ValidationError
from app.repositories.user_repository import UserRepository
from app.schemas.users import AdminUserCreate
from app.security.passwords import ensure_not_in_history
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def test_password_history_prevents_reuse(db_session):
    participant = UserRepository(db_session).get_by_username("participant_demo")
    hashes = [item.password_hash for item in UserRepository(db_session).list_password_history(participant.id)]
    with pytest.raises(ValidationError):
        ensure_not_in_history("Participant#2026", hashes)


def test_password_history_depth_blocks_last_five_only(db_session):
    user_repo = UserRepository(db_session)
    auth_service = AuthService(db_session)
    participant = user_repo.get_by_username("participant_demo")

    passwords = [
        "Participant#2026",
        "Participant#2027",
        "Participant#2028",
        "Participant#2029",
        "Participant#2030",
        "Participant#2031",
    ]

    current = passwords[0]
    for next_password in passwords[1:]:
        auth_service.change_password(participant, current, next_password)
        participant = user_repo.get_by_username("participant_demo")
        current = next_password

    with pytest.raises(ValidationError):
        auth_service.change_password(participant, passwords[-1], passwords[1])

    auth_service.change_password(participant, passwords[-1], passwords[0])


def test_admin_created_user_initial_password_is_tracked_in_history(db_session):
    user_repo = UserRepository(db_session)
    auth_service = AuthService(db_session)
    admin = user_repo.get_by_username("admin_demo")
    created = UserService(db_session).create_user(
        admin,
        AdminUserCreate(
            username="admin_created_history",
            full_name="Admin Created History",
            password="AdminCreated#2026",
            role="participant",
            email_optional="admin_created_history@example.local",
        ),
    )

    auth_service.admin_reset_password(created, "AdminCreated#2027", admin_user=admin)
    created = user_repo.get_by_username("admin_created_history")

    with pytest.raises(ValidationError):
        auth_service.change_password(created, "AdminCreated#2027", "AdminCreated#2026")
