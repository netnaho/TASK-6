import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlanPhaseInput(BaseModel):
    phase_number: int
    week_start: int
    week_end: int
    objective: str
    calorie_target: int | None = None
    macro_targets_json: dict = Field(default_factory=dict)
    habits_json: list = Field(default_factory=list)
    success_metrics_json: list = Field(default_factory=list)


class PlanCreateRequest(BaseModel):
    title: str
    duration_weeks: int
    goal_category: str
    summary: str | None = None
    phases: list[PlanPhaseInput]


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    participant_id: uuid.UUID
    profile_id: uuid.UUID
    title: str
    duration_weeks: int
    goal_category: str
    status: str
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class PlanVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_id: uuid.UUID
    version_number: int
    summary: str | None
    phase_count: int
    snapshot_json: dict
    change_summary_json: list[dict]
    created_at: datetime
