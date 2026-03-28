import csv
import io
import json
import logging
import uuid
from pathlib import Path

from openpyxl import Workbook, load_workbook

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.declaration import DeclarationPackage
from app.models.import_export import ExportJob, FieldMapping, ImportJob, MaskingPolicy
from app.models.plan import NutritionPlan
from app.models.profile import ParticipantProfile
from app.models.user import User
from app.repositories.import_export_repository import ImportExportRepository
from app.services.audit_service import AuditService
from app.storage.file_manager import FileManager
from app.utils.datetime import utc_now


logger = logging.getLogger(__name__)


class ImportExportService:
    def __init__(self, db):
        self.db = db
        self.repo = ImportExportRepository(db)
        self.files = FileManager()
        self.audit = AuditService(db)
        self.settings = get_settings()

    def create_mapping(self, user, payload):
        mapping = FieldMapping(**payload.model_dump(), created_by=user.username)
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def create_masking_policy(self, user, payload):
        policy = MaskingPolicy(**payload.model_dump(), created_by=user.username)
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    def list_mappings(self):
        return self.repo.list_mappings()

    def list_masking_policies(self):
        return self.repo.list_masking_policies()

    async def import_file(self, user, upload, format_name: str, mapping_id=None, scope_type: str = "declarations"):
        content = await upload.read()
        storage_path, _, checksum = self.files.write_bytes("imports", upload.filename, content)
        rows = self._read_rows(content, format_name)
        rows = self.apply_import_mapping(rows, mapping_id)
        errors: list[dict] = []
        success_count = 0
        failure_count = 0

        for index, row in enumerate(rows, start=1):
            try:
                with self.db.begin_nested():
                    if scope_type == "declarations":
                        self._import_declaration_row(row)
                    elif scope_type == "profiles":
                        self._import_profile_row(row)
                    else:
                        raise ValidationError("Unsupported import scope.")
                success_count += 1
            except Exception as exc:
                failure_count += 1
                errors.append({"row": index, "error": str(exc), "row_data": row})

        error_report_path = None
        if errors:
            error_report_path, _, _ = self.files.write_bytes("imports", f"import-errors-{uuid.uuid4().hex}.json", json.dumps(errors, default=str).encode())

        job = ImportJob(
            created_by=user.id,
            format=format_name,
            mapping_id=mapping_id,
            status="completed",
            row_count=len(rows),
            success_count=success_count,
            failure_count=failure_count,
            checksum_sha256=checksum,
            started_at=utc_now(),
            completed_at=utc_now(),
            error_report_path=error_report_path or storage_path,
        )
        self.db.add(job)
        self.db.flush()
        self.audit.log(actor_user_id=user.id, action_type="data_import", entity_type="import_job", entity_id=str(job.id), metadata={"scope_type": scope_type, "row_count": len(rows), "success_count": success_count, "failure_count": failure_count})
        self.audit.log(actor_user_id=user.id, action_type="import_completed", entity_type="import_job", entity_id=str(job.id), metadata={"scope_type": scope_type, "row_count": len(rows), "success_count": success_count, "failure_count": failure_count})
        logger.info(
            "Data imported",
            extra={
                "job_id": str(job.id),
                "format": format_name,
                "scope_type": scope_type,
                "record_count": len(rows),
                "success_count": success_count,
                "failure_count": failure_count,
            },
        )
        self.db.commit()
        self.db.refresh(job)
        return job

    def export_rows(self, user, format_name: str, scope_type: str, rows: list[dict], masking_policy_id=None, mapping_id=None):
        masked_rows = self.apply_masking(rows, masking_policy_id)
        content, filename = self._write_rows(masked_rows, format_name, scope_type, mapping_id)
        storage_path, _, checksum = self.files.write_bytes("exports", filename, content)
        job = ExportJob(
            created_by=user.id,
            format=format_name,
            scope_type=scope_type,
            masking_policy_id=masking_policy_id,
            status="completed",
            row_count=len(masked_rows),
            checksum_sha256=checksum,
            started_at=utc_now(),
            completed_at=utc_now(),
        )
        self.db.add(job)
        self.db.flush()
        self.audit.log(actor_user_id=user.id, action_type="data_export", entity_type="export_job", entity_id=str(job.id), metadata={"scope_type": scope_type, "row_count": len(masked_rows), "format": format_name})
        logger.info(
            "Data exported",
            extra={"job_id": str(job.id), "format": format_name, "scope_type": scope_type, "record_count": len(masked_rows)},
        )
        self.db.commit()
        self.db.refresh(job)
        return job, storage_path

    def export_scope(self, user, format_name: str, scope_type: str, masking_policy_id=None, mapping_id=None):
        if scope_type == "declarations":
            packages = self.db.query(DeclarationPackage).order_by(DeclarationPackage.created_at.desc()).all()
            rows = [
                {
                    "package_number": item.package_number,
                    "participant_id": str(item.participant_id),
                    "state": str(item.state),
                    "submitted_at": item.submitted_at.isoformat() if item.submitted_at else None,
                    "review_due_at": item.review_due_at.isoformat() if item.review_due_at else None,
                }
                for item in packages
            ]
            return self.export_rows(user, format_name, scope_type, rows, masking_policy_id, mapping_id)
        raise ValidationError("Unsupported export scope.")

    def apply_import_mapping(self, rows: list[dict], mapping_id):
        if not mapping_id:
            return rows
        mapping = self.repo.get_mapping(mapping_id)
        if not mapping:
            raise NotFoundError("Field mapping not found.")
        reverse_mapping = {str(value): key for key, value in mapping.mapping_json.items()}
        transformed: list[dict] = []
        for row in rows:
            transformed.append({reverse_mapping.get(key, key): value for key, value in row.items()})
        return transformed

    def apply_export_mapping(self, rows: list[dict], mapping_id):
        if not mapping_id:
            return rows
        mapping = self.repo.get_mapping(mapping_id)
        if not mapping:
            raise NotFoundError("Field mapping not found.")
        transformed: list[dict] = []
        for row in rows:
            transformed.append({mapping.mapping_json.get(key, key): value for key, value in row.items()})
        return transformed

    def apply_masking(self, rows: list[dict], masking_policy_id):
        if not masking_policy_id:
            return rows
        policy = self.repo.get_masking_policy(masking_policy_id)
        if not policy:
            raise NotFoundError("Masking policy not found.")
        rules = policy.rules_json
        masked_rows: list[dict] = []
        for row in rows:
            masked = dict(row)
            for field in rules.get("mask_fields", []):
                if field in masked:
                    masked[field] = self.settings.export_mask
            masked_rows.append(masked)
        return masked_rows

    def _read_rows(self, content: bytes, format_name: str) -> list[dict]:
        if format_name == "csv":
            text = content.decode()
            return list(csv.DictReader(io.StringIO(text)))
        if format_name == "xlsx":
            workbook = load_workbook(io.BytesIO(content))
            sheet = workbook.active
            if sheet is None:
                return []
            headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                rows.append({headers[i]: row[i] for i in range(len(headers))})
            return rows
        raise ValidationError("Unsupported format.")

    def _write_rows(self, rows: list[dict], format_name: str, scope_type: str, mapping_id=None) -> tuple[bytes, str]:
        rows = self.apply_export_mapping(rows, mapping_id)
        if format_name == "csv":
            stream = io.StringIO()
            writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()) if rows else ["empty"])
            writer.writeheader()
            if rows:
                writer.writerows(rows)
            return stream.getvalue().encode(), f"{scope_type}.csv"
        if format_name == "xlsx":
            workbook = Workbook()
            sheet = workbook.active
            if sheet is None:
                raise ValidationError("Unable to create workbook sheet.")
            headers = list(rows[0].keys()) if rows else ["empty"]
            sheet.append(headers)
            for row in rows:
                sheet.append([row.get(header) for header in headers])
            buffer = io.BytesIO()
            workbook.save(buffer)
            return buffer.getvalue(), f"{scope_type}.xlsx"
        raise ValidationError("Unsupported format.")

    def _import_declaration_row(self, row: dict) -> None:
        participant_id = row.get("participant_id")
        if not participant_id:
            raise ValidationError("participant_id is required for declaration import.")
        participant = self.db.query(User).filter(User.id == participant_id).one_or_none()
        if not participant:
            raise ValidationError("Referenced participant does not exist.")
        profile_id = row.get("profile_id")
        plan_id = row.get("plan_id")
        profile = self.db.query(ParticipantProfile).filter(ParticipantProfile.id == profile_id, ParticipantProfile.user_id == participant.id).one_or_none()
        plan = self.db.query(NutritionPlan).filter(NutritionPlan.id == plan_id, NutritionPlan.participant_id == participant.id).one_or_none()
        if not profile:
            raise ValidationError("Imported declaration requires a valid profile_id for the participant.")
        if not plan:
            raise ValidationError("Imported declaration requires a valid plan_id for the participant.")
        package = DeclarationPackage(
            package_number=row.get("package_number") or f"IMPORTED-{uuid.uuid4().hex[:10].upper()}",
            participant_id=participant.id,
            profile_id=profile.id,
            plan_id=plan.id,
            state=row.get("state", "draft"),
        )
        self.db.add(package)
        self.db.flush()

    def _import_profile_row(self, row: dict) -> None:
        user_id = row.get("user_id")
        if not user_id:
            raise ValidationError("user_id is required for profile import.")
        profile = self.db.query(ParticipantProfile).filter(ParticipantProfile.user_id == user_id).one_or_none()
        payload = {
            "profile_status": row.get("profile_status", "in_progress"),
            "demographics_json": row.get("demographics_json") or {},
            "medical_flags_json": row.get("medical_flags_json") or {},
            "activity_json": row.get("activity_json") or {},
            "anthropometrics_json": row.get("anthropometrics_json") or {},
        }
        if profile:
            for key, value in payload.items():
                setattr(profile, key, value)
            self.db.add(profile)
        else:
            self.db.add(ParticipantProfile(user_id=user_id, **payload))
        self.db.flush()
