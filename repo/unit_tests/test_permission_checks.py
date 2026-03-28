import pytest

from app.core.exceptions import AuthorizationError
from app.core.constants import Role, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.declaration_service import DeclarationService
from app.security.permissions import ensure_package_access


def test_permission_checks_restrict_unrelated_reviewer(db_session):
    users = UserRepository(db_session)
    package = DeclarationService(db_session).list_for_user(users.get_by_username("participant_demo"))[0]
    admin = users.get_by_username("admin_demo")
    assigned_reviewer = users.get_by_username("reviewer_demo")
    unrelated_reviewer = User(
        username="reviewer_other",
        full_name="Other Reviewer",
        email_optional="reviewer_other@example.local",
        role=Role.REVIEWER,
        status=UserStatus.ACTIVE,
        password_hash="placeholder",
        is_active=True,
    )
    db_session.add(unrelated_reviewer)
    db_session.commit()
    ensure_package_access(admin, package)
    ensure_package_access(assigned_reviewer, package)
    with pytest.raises(AuthorizationError):
        ensure_package_access(unrelated_reviewer, package)
