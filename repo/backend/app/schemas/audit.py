import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: uuid.UUID
    occurred_at: datetime
    actor_user_id: uuid.UUID | None
    action_type: str
    entity_type: str
    entity_id: str
    metadata_json: dict
    previous_hash: str | None
    entry_hash: str
