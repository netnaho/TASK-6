import uuid

from pydantic import BaseModel

from app.core.constants import EntityType, ExportScopeType, ImportExportFormat


class MappingCreateRequest(BaseModel):
    name: str
    entity_type: EntityType
    format: ImportExportFormat
    mapping_json: dict


class MaskingPolicyCreateRequest(BaseModel):
    name: str
    entity_type: EntityType
    rules_json: dict
    is_default: bool = False


class ExportRequest(BaseModel):
    format: ImportExportFormat
    scope_type: ExportScopeType
    masking_policy_id: uuid.UUID | None = None
    mapping_id: uuid.UUID | None = None


class ImportRequestMeta(BaseModel):
    format: ImportExportFormat
    mapping_id: uuid.UUID | None = None


class ImportJobDetailRead(BaseModel):
    job: dict
    source_file: dict | None = None
    errors: list[dict] = []
    preview_rows: list[dict] = []


class ExportJobDetailRead(BaseModel):
    job: dict
    output_file: dict | None = None
    preview_rows: list[dict] = []
