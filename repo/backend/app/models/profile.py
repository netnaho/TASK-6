import json
import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.security.encryption import PgcryptoEncryptedJSON, PgcryptoEncryptedText


class ParticipantProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "participant_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    profile_status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_progress")
    demographics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    medical_flags_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    activity_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    anthropometrics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    encrypted_payload: Mapped[str | None] = mapped_column(PgcryptoEncryptedText(), nullable=True)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profile_versions.id"), nullable=True)

    user = relationship("User", back_populates="profile")
    versions: Mapped[list["ParticipantProfileVersion"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        foreign_keys="ParticipantProfileVersion.profile_id",
        order_by=lambda: ParticipantProfileVersion.version_number.desc(),
    )

    @property
    def sensitive(self) -> dict:
        if not self.encrypted_payload:
            return {}
        return json.loads(self.encrypted_payload)


class ParticipantProfileVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "participant_profile_versions"

    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("participant_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(PgcryptoEncryptedJSON(), nullable=False)
    change_summary_json: Mapped[list[dict]] = mapped_column(PgcryptoEncryptedJSON(), nullable=False, default=list)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    profile: Mapped[ParticipantProfile] = relationship(back_populates="versions", foreign_keys=[profile_id])
