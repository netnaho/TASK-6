import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: uuid.UUID
    type: str
    severity: str
    title: str
    message: str
    link_path: str | None
    is_read: bool
    created_at: datetime
