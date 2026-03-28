import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.constants import Role, UserStatus


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    email_optional: str | None
    role: Role
    status: UserStatus
    is_active: bool
    force_password_change: bool
    created_at: datetime


class NotificationPreferencesUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status_changes_enabled: bool | None = None
    mentions_enabled: bool | None = None
    review_requests_enabled: bool | None = None
    deadline_warnings_enabled: bool | None = None


class AdminUserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: Role
    email_optional: str | None = None


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    status: UserStatus | None = None
    role: Role | None = None
    disabled_reason: str | None = None


class AdminPasswordResetRequest(BaseModel):
    new_password: str
