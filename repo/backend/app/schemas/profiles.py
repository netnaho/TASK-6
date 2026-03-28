import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ProfileStatus


class SensitiveProfilePayload(BaseModel):
    diagnoses_notes: str | None = None
    medications_detail: str | None = None
    allergy_detail: str | None = None
    pregnancy_detail: str | None = None
    clinician_notes: str | None = None
    sensitive_free_text: str | None = None


class ProfileUpsertRequest(BaseModel):
    profile_status: ProfileStatus = ProfileStatus.IN_PROGRESS
    demographics_json: dict = Field(default_factory=dict)
    medical_flags_json: dict = Field(default_factory=dict)
    activity_json: dict = Field(default_factory=dict)
    anthropometrics_json: dict = Field(default_factory=dict)
    sensitive: SensitiveProfilePayload = Field(default_factory=SensitiveProfilePayload)


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    profile_status: ProfileStatus
    demographics_json: dict
    medical_flags_json: dict
    activity_json: dict
    anthropometrics_json: dict
    sensitive: dict
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class ProfileVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    profile_id: uuid.UUID
    version_number: int
    snapshot_json: dict
    change_summary_json: list[dict]
    created_at: datetime
