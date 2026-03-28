from sqlalchemy import select

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository):
    def stmt_for_user(self, user_id):
        return select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())

    def list_for_user(self, user_id):
        return self.list_scalars(self.stmt_for_user(user_id))

    def get(self, notification_id):
        return self.scalar_one_or_none(select(Notification).where(Notification.id == notification_id))
