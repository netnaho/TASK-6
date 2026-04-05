import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DeliveryFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "delivery_files"

    package_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=True, index=True)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allowed_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DownloadToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "download_tokens"

    package_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=True, index=True)
    delivery_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_files.id", ondelete="CASCADE"), nullable=False)
    issued_to_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    issued_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)


class AcceptanceConfirmation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "acceptance_confirmations"

    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("declaration_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    confirmed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    delivery_file_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_files.id", ondelete="SET NULL"), nullable=True, index=True)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmation_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted_delivery_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
