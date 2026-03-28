import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Role, UserStatus
from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


enum_values = lambda enum_cls: [item.value for item in enum_cls]


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email_optional: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role_enum", values_callable=enum_values), nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status_enum", values_callable=enum_values), nullable=False, default=UserStatus.ACTIVE)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    force_password_change: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    disabled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    captcha_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    password_history: Mapped[list["PasswordHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notification_preferences: Mapped["NotificationPreference | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile: Mapped["ParticipantProfile | None"] = relationship(back_populates="user", uselist=False)


class NotificationPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    status_changes_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mentions_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    review_requests_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deadline_warnings_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship(back_populates="notification_preferences")


from app.models.auth import PasswordHistory, RefreshToken  # noqa: E402
from app.models.profile import ParticipantProfile  # noqa: E402
