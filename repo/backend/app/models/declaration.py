import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CorrectionStatus, DeclarationState, ReviewAssignmentStatus
from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


enum_values = lambda enum_cls: [item.value for item in enum_cls]


class DeclarationPackage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "declaration_packages"

    package_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    participant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profiles.id"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plans.id"), nullable=False)
    current_plan_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plan_versions.id"), nullable=True)
    current_profile_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profile_versions.id"), nullable=True)
    state: Mapped[DeclarationState] = mapped_column(Enum(DeclarationState, name="declaration_state_enum", values_callable=enum_values), nullable=False, default=DeclarationState.DRAFT)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_review_assignment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("review_assignments.id"), nullable=True)

    versions: Mapped[list["PackageVersion"]] = relationship(back_populates="package", cascade="all, delete-orphan", order_by=lambda: PackageVersion.version_number.desc())
    state_history: Mapped[list["DeclarationStateHistory"]] = relationship(back_populates="package", cascade="all, delete-orphan", order_by=lambda: DeclarationStateHistory.changed_at.desc())
    correction_requests: Mapped[list["CorrectionRequest"]] = relationship(back_populates="package", cascade="all, delete-orphan")
    assignments: Mapped[list["ReviewAssignment"]] = relationship(back_populates="package", cascade="all, delete-orphan", foreign_keys="ReviewAssignment.package_id")


class PackageVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "package_versions"

    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[DeclarationState] = mapped_column(Enum(DeclarationState, name="package_version_state_enum", values_callable=enum_values), nullable=False)
    profile_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profile_versions.id"), nullable=True)
    plan_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("nutrition_plan_versions.id"), nullable=True)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_summary_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    package: Mapped[DeclarationPackage] = relationship(back_populates="versions")


class DeclarationStateHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "declaration_state_history"

    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    package: Mapped[DeclarationPackage] = relationship(back_populates="state_history")


class ReviewAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "review_assignments"

    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    review_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")
    status: Mapped[ReviewAssignmentStatus] = mapped_column(Enum(ReviewAssignmentStatus, name="review_assignment_status_enum", values_callable=enum_values), nullable=False, default=ReviewAssignmentStatus.QUEUED)

    package: Mapped[DeclarationPackage] = relationship(back_populates="assignments", foreign_keys=[package_id])


class CorrectionRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "correction_requests"

    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    review_assignment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_assignments.id", ondelete="CASCADE"), nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    response_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[CorrectionStatus] = mapped_column(Enum(CorrectionStatus, name="correction_status_enum", values_callable=enum_values), nullable=False, default=CorrectionStatus.OPEN)
    sections_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    overall_message: Mapped[str] = mapped_column(Text, nullable=False)
    participant_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    participant_resubmitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    package: Mapped[DeclarationPackage] = relationship(back_populates="correction_requests")
