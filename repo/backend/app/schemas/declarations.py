import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.constants import DeclarationState


class DeclarationCreateRequest(BaseModel):
    profile_id: uuid.UUID
    plan_id: uuid.UUID


class StateChangeRequest(BaseModel):
    reason_code: str | None = None
    reason_text: str | None = None


class DeclarationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    package_number: str
    participant_id: uuid.UUID
    profile_id: uuid.UUID
    plan_id: uuid.UUID
    state: DeclarationState
    submitted_at: datetime | None
    withdrawn_at: datetime | None
    voided_at: datetime | None
    accepted_at: datetime | None
    review_due_at: datetime | None
    current_review_assignment_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class PackageVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    package_id: uuid.UUID
    version_number: int
    state: DeclarationState
    profile_version_id: uuid.UUID | None
    plan_version_id: uuid.UUID | None
    snapshot_json: dict
    change_summary_json: list[dict]
    created_at: datetime


class CorrectionRequestCreate(BaseModel):
    overall_message: str
    sections_json: list[dict]
    response_due_hours: int = 72


class CorrectionAcknowledgeRequest(BaseModel):
    note: str | None = None


class CorrectionResubmitRequest(BaseModel):
    reason_text: str | None = None
