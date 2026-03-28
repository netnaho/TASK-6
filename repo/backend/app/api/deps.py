from typing import Annotated

from fastapi import Depends, Header, Request
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.constants import UserStatus
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.security.permissions import require_role
from app.security.tokens import decode_access_token
from app.services.auth_service import AuthService


DBSession = Annotated[Session, Depends(get_db)]


def _get_current_user(request: Request, db: DBSession, authorization: Annotated[str | None, Header()] = None, *, allow_force_change: bool = False):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Missing bearer token.")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise AuthenticationError("Invalid access token.") from exc
    user = UserRepository(db).get_by_id(payload["sub"])
    if not user:
        raise AuthenticationError("User not found.")
    AuthService.ensure_user_active(user)
    if user.force_password_change and not allow_force_change:
        raise AuthorizationError("Password change required before accessing other resources.")
    request.state.user = user
    return user


def get_current_user(request: Request, db: DBSession, authorization: Annotated[str | None, Header()] = None):
    return _get_current_user(request, db, authorization, allow_force_change=False)


def get_current_user_allow_force_change(request: Request, db: DBSession, authorization: Annotated[str | None, Header()] = None):
    return _get_current_user(request, db, authorization, allow_force_change=True)


def require_roles(*roles):
    def dependency(user=Depends(get_current_user)):
        require_role(user.role, list(roles))
        return user

    return dependency
