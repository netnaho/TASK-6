import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import DBSession, require_roles
from app.core.constants import ExportScopeType, ImportExportFormat, Role
from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.imports_exports import ExportRequest, MappingCreateRequest, MaskingPolicyCreateRequest
from app.services.import_export_service import ImportExportService

router = APIRouter()


@router.post("/imports")
async def create_import(
    format: ImportExportFormat = Form(...),
    scope_type: ExportScopeType = Form(ExportScopeType.DECLARATIONS),
    mapping_id: uuid.UUID | None = Form(None),
    upload: UploadFile = File(...),
    db=Depends(get_db),
    user=Depends(require_roles(Role.ADMINISTRATOR)),
):
    job = await ImportExportService(db).import_file(user, upload, format, mapping_id, scope_type)
    return success_response(job, "Import completed")


@router.get("/imports")
def list_imports(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).repo.list_imports())


@router.post("/exports")
def create_export(payload: ExportRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    job = ImportExportService(db).export_scope(user, payload.format, payload.scope_type, payload.masking_policy_id, payload.mapping_id)
    return success_response(job, "Export completed")


@router.get("/exports")
def list_exports(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).repo.list_exports())


@router.get("/imports/{job_id}")
def get_import(job_id: str, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).get_import_detail(job_id))


@router.get("/imports/{job_id}/source-download-link")
def import_source_download_link(job_id: str, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).create_import_source_download_link(user, job_id), "Import source download link created")


@router.get("/exports/{job_id}")
def get_export(job_id: str, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).get_export_detail(job_id))


@router.get("/exports/{job_id}/download-link")
def export_download_link(job_id: str, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).create_export_download_link(user, job_id), "Export download link created")


@router.get("/admin/field-mappings")
def list_field_mappings(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).list_mappings())


@router.post("/admin/field-mappings")
def create_field_mapping(payload: MappingCreateRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).create_mapping(user, payload), "Field mapping created")


@router.get("/admin/masking-policies")
def list_masking_policies(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).list_masking_policies())


@router.post("/admin/masking-policies")
def create_masking_policy(payload: MaskingPolicyCreateRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(ImportExportService(db).create_masking_policy(user, payload), "Masking policy created")
