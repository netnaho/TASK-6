import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class NutritionPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "nutrition_plans"

    participant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profiles.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    goal_category: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plan_versions.id"), nullable=True)

    versions: Mapped[list["NutritionPlanVersion"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        foreign_keys="NutritionPlanVersion.plan_id",
        order_by=lambda: NutritionPlanVersion.version_number.desc(),
    )


class NutritionPlanVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "nutrition_plan_versions"

    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    phase_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_summary_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped[NutritionPlan] = relationship(back_populates="versions", foreign_keys=[plan_id])
    phases: Mapped[list["PlanPhase"]] = relationship(back_populates="plan_version", cascade="all, delete-orphan")


class PlanPhase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "plan_phases"

    plan_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plan_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False)
    week_start: Mapped[int] = mapped_column(Integer, nullable=False)
    week_end: Mapped[int] = mapped_column(Integer, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    calorie_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    macro_targets_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    habits_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    success_metrics_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    plan_version: Mapped[NutritionPlanVersion] = relationship(back_populates="phases")
