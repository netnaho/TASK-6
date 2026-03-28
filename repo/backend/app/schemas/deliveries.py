import uuid
from datetime import datetime

from pydantic import BaseModel


class DeliveryLinkRequest(BaseModel):
    delivery_file_id: uuid.UUID
    expires_in_hours: int | None = None
    purpose: str = "download"


class AcceptanceRequest(BaseModel):
    confirmation_note: str | None = None
    accepted_delivery_version: str | None = None


class DeliveryFileRead(BaseModel):
    id: uuid.UUID
    package_id: uuid.UUID
    file_type: str
    display_name: str
    mime_type: str
    checksum_sha256: str
    size_bytes: int
    version_label: str | None
    is_final: bool
    created_at: datetime
