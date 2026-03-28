from app.core.constants import Role
from app.core.exceptions import AuthorizationError


def require_role(user_role: str, allowed_roles: list[Role]) -> None:
    if user_role not in allowed_roles:
        raise AuthorizationError()


def ensure_package_access(user, package) -> None:
    if user.role == Role.ADMINISTRATOR:
        return
    if user.role == Role.REVIEWER and getattr(package, "assignments", None):
        if any(str(assignment.reviewer_id) == str(user.id) for assignment in package.assignments):
            return
    if user.role == Role.PARTICIPANT and package.participant_id == user.id:
        return
    raise AuthorizationError("You do not have permission to access this package.")


def ensure_package_owner(user, package) -> None:
    if user.role == Role.PARTICIPANT and package.participant_id == user.id:
        return
    raise AuthorizationError("You do not have permission to modify this package.")


def ensure_plan_owner(user, plan) -> None:
    if user.role == Role.PARTICIPANT and plan.participant_id == user.id:
        return
    raise AuthorizationError("You do not have permission to access this plan.")


def ensure_profile_owner(user, profile) -> None:
    if user.role == Role.PARTICIPANT and profile.user_id == user.id:
        return
    raise AuthorizationError("You do not have permission to access this profile.")
