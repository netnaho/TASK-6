import re

from sqlalchemy import select

from app.core.constants import NotificationSeverity, NotificationType
from app.models.notification import Mention, Notification
from app.models.user import NotificationPreference, User
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.utils.datetime import add_days


MENTION_PATTERN = re.compile(r"(?<!\w)@([A-Za-z0-9_][A-Za-z0-9_.-]{1,49})")


class NotificationService:
    def __init__(self, db):
        self.db = db
        self.repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    def _is_muted(self, user_id, notification_type: str) -> bool:
        if notification_type == NotificationType.MANDATORY_COMPLIANCE_ALERT:
            return False
        prefs = self.user_repo.get_preferences(user_id)
        if not prefs:
            return False
        mapping = {
            NotificationType.STATUS_CHANGE: prefs.status_changes_enabled,
            NotificationType.MENTION: prefs.mentions_enabled,
            NotificationType.REVIEW_REQUEST: prefs.review_requests_enabled,
            NotificationType.DEADLINE_WARNING: prefs.deadline_warnings_enabled,
        }
        key = NotificationType(notification_type) if not isinstance(notification_type, NotificationType) else notification_type
        return not mapping.get(key, True)

    def create(self, *, user_id, notification_type: str, severity: str, title: str, message: str, link_path: str | None = None):
        muted = self._is_muted(user_id, notification_type)
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            severity=severity,
            title=title,
            message=message,
            link_path=link_path,
            is_muted_snapshot=muted,
            expires_at=add_days(90),
        )
        self.db.add(notification)
        return notification

    def create_once(self, *, user_id, notification_type: str, severity: str, title: str, message: str, link_path: str | None = None):
        existing = self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.type == str(notification_type),
                Notification.title == title,
                Notification.message == message,
                Notification.link_path == link_path,
            )
        ).scalar_one_or_none()
        if existing:
            return existing, False
        return self.create(
            user_id=user_id,
            notification_type=notification_type,
            severity=severity,
            title=title,
            message=message,
            link_path=link_path,
        ), True

    @staticmethod
    def extract_mentions(*texts: str | None) -> list[str]:
        usernames: set[str] = set()
        for text in texts:
            if not text:
                continue
            usernames.update(match.group(1) for match in MENTION_PATTERN.finditer(text))
        return sorted(usernames)

    def create_mentions(self, *, source_type: str, source_id, mentioned_by: User, texts: list[str], link_path: str | None = None):
        usernames = self.extract_mentions(*texts)
        if not usernames:
            return []

        users = self.db.execute(
            select(User).where(User.username.in_(usernames), User.is_active.is_(True))
        ).scalars().all()

        created_notifications = []
        for user in users:
            if str(user.id) == str(mentioned_by.id):
                continue
            title = f"Mention from {mentioned_by.username}"
            message = f"{mentioned_by.username} mentioned you in {source_type.replace('_', ' ')} feedback."
            notification, created = self.create_once(
                user_id=user.id,
                notification_type=NotificationType.MENTION,
                severity=NotificationSeverity.INFO,
                title=title,
                message=message,
                link_path=link_path,
            )
            if created:
                self.db.flush()
                self.db.add(
                    Mention(
                        notification_id=notification.id,
                        source_type=source_type,
                        source_id=source_id,
                        mentioned_by=mentioned_by.id,
                        mentioned_user_id=user.id,
                    )
                )
                created_notifications.append(notification)
        return created_notifications

    def create_deadline_warning(self, *, user_id, title: str, message: str, link_path: str | None = None):
        return self.create_once(
            user_id=user_id,
            notification_type=NotificationType.DEADLINE_WARNING,
            severity=NotificationSeverity.WARNING,
            title=title,
            message=message,
            link_path=link_path,
        )[0]

    def list_for_user(self, user_id):
        return self.repo.list_for_user(user_id)

    def get_preferences(self, user_id):
        prefs = self.user_repo.get_preferences(user_id)
        if prefs:
            return prefs
        prefs = NotificationPreference(user_id=user_id)
        self.db.add(prefs)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs
