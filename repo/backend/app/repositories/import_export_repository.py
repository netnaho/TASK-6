from sqlalchemy import select

from app.models.import_export import ExportJob, FieldMapping, ImportJob, MaskingPolicy
from app.repositories.base import BaseRepository


class ImportExportRepository(BaseRepository):
    def get_mapping(self, mapping_id):
        return self.scalar_one_or_none(select(FieldMapping).where(FieldMapping.id == mapping_id))

    def list_mappings(self):
        return self.list_scalars(select(FieldMapping).order_by(FieldMapping.created_at.desc()))

    def get_masking_policy(self, policy_id):
        return self.scalar_one_or_none(select(MaskingPolicy).where(MaskingPolicy.id == policy_id))

    def list_masking_policies(self):
        return self.list_scalars(select(MaskingPolicy).order_by(MaskingPolicy.created_at.desc()))

    def list_imports(self):
        return self.list_scalars(select(ImportJob).order_by(ImportJob.created_at.desc()))

    def get_import(self, job_id):
        return self.scalar_one_or_none(select(ImportJob).where(ImportJob.id == job_id))

    def list_exports(self):
        return self.list_scalars(select(ExportJob).order_by(ExportJob.created_at.desc()))

    def get_export(self, job_id):
        return self.scalar_one_or_none(select(ExportJob).where(ExportJob.id == job_id))
