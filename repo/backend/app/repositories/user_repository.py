from sqlalchemy import select

from app.models.auth import PasswordHistory, RefreshToken
from app.models.user import NotificationPreference, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_username(self, username: str) -> User | None:
        return self.scalar_one_or_none(select(User).where(User.username == username))

    def get_by_id(self, user_id):
        return self.scalar_one_or_none(select(User).where(User.id == user_id))

    def list_password_history(self, user_id):
        stmt = select(PasswordHistory).where(PasswordHistory.user_id == user_id).order_by(PasswordHistory.created_at.desc())
        return self.list_scalars(stmt)

    def get_refresh_token(self, token_hash: str):
        return self.scalar_one_or_none(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    def get_preferences(self, user_id):
        return self.scalar_one_or_none(select(NotificationPreference).where(NotificationPreference.user_id == user_id))
