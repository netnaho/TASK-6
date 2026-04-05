from app.core.constants import UserStatus
from app.core.exceptions import NotFoundError
from app.models.auth import PasswordHistory
from app.models.user import NotificationPreference, User
from app.repositories.user_repository import UserRepository
from app.schemas.users import NotificationPreferencesUpdate
from app.security.passwords import hash_password, validate_password_policy
from app.services.audit_service import AuditService
from app.utils.datetime import utc_now


class UserService:
    PREFERENCE_FIELDS = (
        "status_changes_enabled",
        "mentions_enabled",
        "review_requests_enabled",
        "deadline_warnings_enabled",
    )

    def __init__(self, db):
        self.db = db
        self.repo = UserRepository(db)
        self.audit = AuditService(db)

    def get_user(self, user_id):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    def update_preferences(self, user_id, payload: NotificationPreferencesUpdate):
        prefs = self.repo.get_preferences(user_id)
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            self.db.add(prefs)

        for key, value in payload.model_dump(exclude_none=True).items():
            if key in self.PREFERENCE_FIELDS:
                setattr(prefs, key, value)

        self.db.add(prefs)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    def create_user(self, actor, payload):
        validate_password_policy(payload.password)
        password_hash = hash_password(payload.password)
        user = User(
            username=payload.username,
            full_name=payload.full_name,
            email_optional=payload.email_optional,
            role=payload.role,
            status=UserStatus.ACTIVE,
            password_hash=password_hash,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        self.db.add(NotificationPreference(user_id=user.id))
        self.db.add(PasswordHistory(user_id=user.id, password_hash=password_hash, created_at=utc_now()))
        self.audit.log(actor_user_id=actor.id, action_type="admin_user_create", entity_type="user", entity_id=str(user.id), metadata={"role": user.role})
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, actor, user_id, payload):
        user = self.get_user(user_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        self.db.add(user)
        self.audit.log(actor_user_id=actor.id, action_type="admin_user_update", entity_type="user", entity_id=str(user.id), metadata=payload.model_dump(exclude_none=True))
        self.db.commit()
        self.db.refresh(user)
        return user
