import io
import logging
import zipfile

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.constants import DeclarationState, DeliveryFileType, Role
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError, NotFoundError
from app.models.delivery import AcceptanceConfirmation, DeliveryFile, DownloadToken
from app.repositories.declaration_repository import DeclarationRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.user_repository import UserRepository
from app.security.permissions import ensure_delivery_file_access, ensure_package_access, ensure_package_owner
from app.security.tokens import generate_download_token, hash_download_token
from app.services.audit_service import AuditService
from app.services.runtime_settings_service import RuntimeSettingsService
from app.storage.file_manager import FileManager
from app.storage.pdf_generator import render_plan_pdf
from app.utils.datetime import add_hours, utc_now


logger = logging.getLogger(__name__)


class DeliveryService:
    def __init__(self, db):
        self.db = db
        self.repo = DeliveryRepository(db)
        self.package_repo = DeclarationRepository(db)
        self.user_repo = UserRepository(db)
        self.files = FileManager()
        self.audit = AuditService(db)
        self.settings = get_settings()
        self.runtime_settings = RuntimeSettingsService(db)

    def _download_expiry_hours(self) -> int:
        value = self.runtime_settings.get("default_download_expiry_hours", self.settings.default_download_expiry_hours)
        if isinstance(value, bool):
            return int(self.settings.default_download_expiry_hours)
        if isinstance(value, (int, float, str)):
            return int(value)
        return int(self.settings.default_download_expiry_hours)

    def list_files(self, user, package_id):
        package = self.package_repo.get(package_id)
        if not package:
            raise NotFoundError("Package not found.")
        ensure_package_access(user, package)
        return [file for file in self.repo.list_files(package_id) if self._can_access_file(user, file)]

    @staticmethod
    def _ensure_delivery_publisher(user) -> None:
        if user.role not in {Role.REVIEWER, Role.ADMINISTRATOR}:
            raise AuthorizationError("Only reviewers and administrators can publish delivery artifacts or secure links.")

    @staticmethod
    def _normalize_roles(allowed_roles: list[str] | None, default_roles: list[str] | None = None) -> list[str]:
        raw_roles = allowed_roles if allowed_roles is not None else default_roles or [Role.PARTICIPANT, Role.REVIEWER, Role.ADMINISTRATOR]
        normalized = []
        for role in raw_roles:
            value = str(role)
            if value in {Role.PARTICIPANT, Role.REVIEWER, Role.ADMINISTRATOR} and value not in normalized:
                normalized.append(value)
        if not normalized:
            raise AuthorizationError("At least one delivery audience role is required.")
        return normalized

    @staticmethod
    def _can_access_file(user, file: DeliveryFile) -> bool:
        try:
            ensure_delivery_file_access(user, file)
            return True
        except AuthorizationError:
            return False

    def _target_role_for_link(self, current_user, participant_id, issued_to_user_id) -> str:
        if str(issued_to_user_id) == str(participant_id):
            return Role.PARTICIPANT
        if str(issued_to_user_id) == str(current_user.id):
            return str(current_user.role)
        target_user = self.user_repo.get_by_id(issued_to_user_id)
        if not target_user:
            raise NotFoundError("Target user not found.")
        if current_user.role != Role.ADMINISTRATOR:
            raise AuthorizationError("Only administrators can issue delivery links to other users.")
        return str(target_user.role)

    def _create_token(self, *, file: DeliveryFile, issued_to_user_id, issued_by: str, purpose: str, expires_in_hours: int | None = None):
        raw = generate_download_token()
        expires_at = add_hours(expires_in_hours or self._download_expiry_hours())
        token = DownloadToken(
            package_id=file.package_id,
            delivery_file_id=file.id,
            issued_to_user_id=issued_to_user_id,
            token_hash=hash_download_token(raw),
            expires_at=expires_at,
            issued_by=issued_by,
            purpose=purpose,
        )
        self.db.add(token)
        self.db.flush()
        return {"token": raw, "expires_at": expires_at.isoformat(), "delivery_file_id": str(file.id)}

    async def upload_file(self, user, package_id, upload: UploadFile, file_type: str, is_final: bool = False, allowed_roles: list[str] | None = None):
        package = self.package_repo.get(package_id)
        if not package:
            raise NotFoundError("Package not found.")
        self._ensure_delivery_publisher(user)
        ensure_package_access(user, package)
        content = await upload.read()
        storage_path, size_bytes, checksum = self.files.write_bytes("deliveries", upload.filename, content)
        file = DeliveryFile(
            package_id=package_id,
            file_type=file_type,
            display_name=upload.filename,
            storage_path=storage_path,
            mime_type=upload.content_type or "application/octet-stream",
            checksum_sha256=checksum,
            size_bytes=size_bytes,
            version_label="uploaded",
            is_final=is_final,
            allowed_roles=self._normalize_roles(allowed_roles),
            created_by=user.username,
        )
        self.db.add(file)
        self.audit.log(actor_user_id=user.id, action_type="delivery_upload", entity_type="delivery_file", entity_id=str(file.id), metadata={"package_id": str(package_id)})
        self.db.commit()
        self.db.refresh(file)
        return file

    def generate_final_pdf(self, user, package_id, participant_name: str, plan_title: str, summary: str):
        self._ensure_delivery_publisher(user)
        content = render_plan_pdf(plan_title, participant_name, summary)
        storage_path, size_bytes, checksum = self.files.write_bytes("deliveries", f"{plan_title}.pdf", content)
        file = DeliveryFile(
            package_id=package_id,
            file_type=DeliveryFileType.FINAL_PLAN_PDF,
            display_name=f"{plan_title}.pdf",
            storage_path=storage_path,
            mime_type="application/pdf",
            checksum_sha256=checksum,
            size_bytes=size_bytes,
            version_label="final",
            is_final=True,
            allowed_roles=[Role.PARTICIPANT, Role.REVIEWER, Role.ADMINISTRATOR],
            created_by=user.username,
        )
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def create_download_link(self, user, package_id, delivery_file_id, expires_in_hours: int | None, purpose: str, issued_to_user_id=None):
        package = self.package_repo.get(package_id)
        if not package:
            raise NotFoundError("Package not found.")
        self._ensure_delivery_publisher(user)
        ensure_package_access(user, package)
        file = self.repo.get_file_for_package(package_id, delivery_file_id)
        if not file:
            file = self.repo.get_file(delivery_file_id)
            if not file:
                raise NotFoundError("Delivery file not found.")
            raise ConflictError("Delivery file does not belong to the selected package.")
        target_user_id = issued_to_user_id or package.participant_id
        target_role = self._target_role_for_link(user, package.participant_id, target_user_id)
        if target_role not in self._normalize_roles(file.allowed_roles):
            raise AuthorizationError("The selected recipient is not permitted to download this file.")
        payload = self._create_token(
            file=file,
            issued_to_user_id=target_user_id,
            issued_by=user.username,
            purpose=purpose,
            expires_in_hours=expires_in_hours,
        )
        self.db.commit()
        logger.info(
            "Download token generated",
            extra={
                "file_id": str(delivery_file_id),
                "user_id": str(user.id),
                "package_id": str(package_id),
                "issued_to_user_id": str(target_user_id),
            },
        )
        return payload

    def create_direct_download_link(self, user, delivery_file_id, *, issued_to_user_id=None, expires_in_hours: int | None = None, purpose: str = "download"):
        file = self.repo.get_file(delivery_file_id)
        if not file:
            raise NotFoundError("Delivery file not found.")
        if file.package_id:
            package = self.package_repo.get(file.package_id)
            if not package:
                raise NotFoundError("Package not found.")
            ensure_package_access(user, package)
        ensure_delivery_file_access(user, file)
        target_user_id = issued_to_user_id or user.id
        target_role = self._target_role_for_link(user, None, target_user_id) if file.package_id is None else str(user.role if str(target_user_id) == str(user.id) else Role.PARTICIPANT)
        if target_role not in self._normalize_roles(file.allowed_roles):
            raise AuthorizationError("The selected recipient is not permitted to download this file.")
        payload = self._create_token(
            file=file,
            issued_to_user_id=target_user_id,
            issued_by=user.username,
            purpose=purpose,
            expires_in_hours=expires_in_hours,
        )
        self.db.commit()
        return payload

    def create_standalone_file(self, *, created_by: str, display_name: str, file_type: str, storage_path: str, mime_type: str, checksum_sha256: str, size_bytes: int, allowed_roles: list[str] | None = None, version_label: str | None = None):
        file = DeliveryFile(
            package_id=None,
            file_type=file_type,
            display_name=display_name,
            storage_path=storage_path,
            mime_type=mime_type,
            checksum_sha256=checksum_sha256,
            size_bytes=size_bytes,
            version_label=version_label,
            is_final=False,
            allowed_roles=self._normalize_roles(allowed_roles, [Role.ADMINISTRATOR]),
            created_by=created_by,
        )
        self.db.add(file)
        self.db.flush()
        return file

    def generate_bulk_package(self, user, package_id):
        package = self.package_repo.get(package_id)
        if not package:
            raise NotFoundError("Package not found.")
        ensure_package_access(user, package)
        files = [file for file in self.repo.list_files(package_id) if self._can_access_file(user, file)]
        if not files:
            raise ConflictError("No delivery files are available for bulk download.")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in files:
                archive.writestr(file.display_name, self.files.read_bytes(file.storage_path))

        content = buffer.getvalue()
        storage_path, size_bytes, checksum = self.files.write_bytes("bulk", f"package-{package.package_number}.zip", content)
        bulk_file = DeliveryFile(
            package_id=package_id,
            file_type=DeliveryFileType.BULK_PACKAGE,
            display_name=f"{package.package_number}-bulk.zip",
            storage_path=storage_path,
            mime_type="application/zip",
            checksum_sha256=checksum,
            size_bytes=size_bytes,
            version_label="bulk",
            is_final=False,
            allowed_roles=[str(user.role)],
            created_by=user.username,
        )
        self.db.add(bulk_file)
        self.db.flush()

        payload = self._create_token(file=bulk_file, issued_to_user_id=user.id, issued_by=user.username, purpose="bulk_download")
        self.audit.log(
            actor_user_id=user.id,
            action_type="bulk_download_package_generated",
            entity_type="declaration",
            entity_id=str(package_id),
            metadata={"delivery_file_id": str(bulk_file.id), "file_count": len(files)},
        )
        self.db.commit()
        logger.info(
            "Download token generated",
            extra={"file_id": str(bulk_file.id), "user_id": str(user.id), "package_id": str(package_id), "purpose": "bulk_download"},
        )
        return payload

    def validate_download(self, user, token_value: str):
        token = self.repo.get_download_token(hash_download_token(token_value))
        if not token or token.revoked_at or token.expires_at < utc_now():
            raise AuthenticationError("Download link is invalid or expired.")
        if str(token.issued_to_user_id) != str(user.id) and user.role != "administrator":
            raise AuthorizationError("Download link is not valid for this user.")
        file = self.repo.get_file(token.delivery_file_id)
        if not file or not self.files.exists(file.storage_path):
            raise NotFoundError("File not found.")
        if file.package_id:
            package = self.package_repo.get(file.package_id)
            if not package:
                raise NotFoundError("Package not found.")
            ensure_package_access(user, package)
        ensure_delivery_file_access(user, file)
        token.used_at = utc_now()
        self.db.add(token)
        self.db.commit()
        return file

    def accept(self, user, package_id, note: str | None, delivery_version: str | None):
        package = self.package_repo.get(package_id)
        if not package:
            raise NotFoundError("Package not found.")
        ensure_package_owner(user, package)
        if package.state == DeclarationState.DRAFT and not self.repo.list_files(package_id):
            raise ConflictError("A delivery artifact is required before acceptance can be recorded.")
        if package.accepted_at is not None:
            raise ConflictError("Delivery acceptance has already been recorded.")
        confirmation = AcceptanceConfirmation(
            package_id=package_id,
            confirmed_by=user.id,
            confirmed_at=utc_now(),
            confirmation_note=note,
            accepted_delivery_version=delivery_version,
        )
        package.accepted_at = utc_now()
        self.db.add(package)
        self.db.add(confirmation)
        self.db.commit()
        logger.info("Delivery accepted", extra={"package_id": str(package_id), "confirmed_by": str(user.id)})
        return confirmation
