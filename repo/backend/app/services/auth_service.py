import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import Role, UserStatus
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError, ValidationError
from app.models.auth import PasswordHistory, RefreshToken
from app.models.user import NotificationPreference, User
from app.repositories.user_repository import UserRepository
from app.security.captcha import verify_captcha
from app.security.passwords import ensure_not_in_history, hash_password, validate_password_policy, verify_password
from app.security.tokens import create_access_token, create_refresh_token, decode_refresh_token, hash_refresh_token
from app.services.audit_service import AuditService
from app.utils.datetime import add_minutes, utc_now


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.repo = UserRepository(db)
        self.audit = AuditService(db)

    def register_participant(self, username: str, full_name: str, password: str, email_optional: str | None = None) -> User:
        if self.repo.get_by_username(username):
            raise ConflictError("Username already exists.")
        validate_password_policy(password)
        password_hash = hash_password(password)
        user = User(
            username=username,
            full_name=full_name,
            email_optional=email_optional,
            role=Role.PARTICIPANT,
            status=UserStatus.ACTIVE,
            password_hash=password_hash,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        self.db.add(NotificationPreference(user_id=user.id))
        self.db.add(PasswordHistory(user_id=user.id, password_hash=password_hash, created_at=utc_now()))
        self.audit.log(actor_user_id=user.id, action_type="register", entity_type="user", entity_id=str(user.id), metadata={"username": username})
        logger.info("New participant registered", extra={"user_id": str(user.id), "username": username})
        self.db.commit()
        self.db.refresh(user)
        return user

    def _check_lockout(self, user: User) -> None:
        if user.locked_until and user.locked_until > utc_now():
            raise AuthenticationError("Account is locked. Try again later.")

    def _register_failed_attempt(self, user: User) -> None:
        user.failed_login_attempts += 1
        logger.warning("Failed login attempt", extra={"user_id": str(user.id), "attempts": user.failed_login_attempts})
        if user.failed_login_attempts >= self.settings.lockout_failed_attempts:
            user.locked_until = add_minutes(self.settings.lockout_minutes)
            logger.warning("Account locked", extra={"user_id": str(user.id), "locked_until": user.locked_until.isoformat()})
        self.db.add(user)
        self.db.commit()

    def login(self, username: str, password: str, *, captcha_challenge_token: str | None = None, captcha_answer: str | None = None, user_agent: str | None = None) -> dict:
        user = self.repo.get_by_username(username)
        if not user:
            raise AuthenticationError("Invalid username or password.")
        self.ensure_user_active(user)
        self._check_lockout(user)
        if self.settings.enable_local_captcha and user.captcha_required:
            if not captcha_challenge_token or not captcha_answer:
                raise ValidationError("CAPTCHA is required.", field="captcha")
            verify_captcha(captcha_challenge_token, captcha_answer)
        if not verify_password(password, user.password_hash):
            self._register_failed_attempt(user)
            raise AuthenticationError("Invalid username or password.")
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = utc_now()
        access = create_access_token(str(user.id), {"role": user.role})
        refresh, refresh_hash, refresh_expires = create_refresh_token(str(user.id))
        self.db.add(RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=refresh_expires, issued_at=utc_now(), user_agent=user_agent))
        self.db.add(user)
        self.audit.log(actor_user_id=user.id, action_type="login", entity_type="user", entity_id=str(user.id), metadata={})
        logger.info("User login successful", extra={"user_id": str(user.id), "username": username})
        self.db.commit()
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "access_expires_in_minutes": self.settings.access_token_expire_minutes,
            "refresh_expires_in_days": self.settings.refresh_token_expire_days,
            "force_password_change": user.force_password_change,
        }

    def refresh(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        token_row = self.repo.get_refresh_token(hash_refresh_token(refresh_token))
        if not token_row or token_row.revoked_at is not None or token_row.expires_at < utc_now():
            raise AuthenticationError("Refresh token is invalid or expired.")
        user = self.repo.get_by_id(token_row.user_id)
        if not user or not user.is_active or user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Session expired or account disabled.")
        token_row.revoked_at = utc_now()
        access = create_access_token(str(user.id), {"role": user.role})
        new_refresh, new_hash, new_exp = create_refresh_token(str(user.id))
        self.db.add(RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=new_exp, issued_at=utc_now(), rotated_from_id=token_row.id))
        self.db.add(token_row)
        self.db.commit()
        return {
            "access_token": access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "access_expires_in_minutes": self.settings.access_token_expire_minutes,
            "refresh_expires_in_days": self.settings.refresh_token_expire_days,
            "force_password_change": user.force_password_change,
        }

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect.")
        self._set_new_password(user, new_password, force_password_change=False)

    def complete_forced_password_change(self, user: User, new_password: str) -> None:
        self._set_new_password(user, new_password, force_password_change=False)

    def admin_reset_password(self, user: User, new_password: str, *, admin_user: User) -> None:
        self._set_new_password(user, new_password, force_password_change=True, actor_user=admin_user)

    def _set_new_password(self, user: User, new_password: str, *, force_password_change: bool, actor_user: User | None = None) -> None:
        validate_password_policy(new_password)
        hashes = [item.password_hash for item in self.repo.list_password_history(user.id)]
        ensure_not_in_history(new_password, hashes)
        new_hash = hash_password(new_password)
        user.password_hash = new_hash
        user.force_password_change = force_password_change
        self.db.add(user)
        self.db.add(PasswordHistory(user_id=user.id, password_hash=new_hash, created_at=utc_now()))
        actor_id = actor_user.id if actor_user else user.id
        metadata = {
            "forced": force_password_change,
            "target_user_id": str(user.id),
            "admin_initiated": actor_user is not None,
        }
        if actor_user is not None:
            metadata["admin_user_id"] = str(actor_user.id)
            metadata["admin_username"] = actor_user.username
        self.audit.log(
            actor_user_id=actor_id,
            action_type="admin_password_reset" if actor_user is not None else "password_change",
            entity_type="user",
            entity_id=str(user.id),
            metadata=metadata,
        )
        logger.info(
            "Password changed",
            extra={
                "user_id": str(user.id),
                "forced": force_password_change,
                "admin_initiated": actor_user is not None,
            },
        )
        self.db.commit()

    @staticmethod
    def ensure_user_active(user: User) -> None:
        if not user or not user.is_active or user.status != UserStatus.ACTIVE:
            raise AuthorizationError("Account is disabled.")
