from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.models.audit import AuditArchive
from app.models.audit import AuditLog
from app.models.settings import SystemSetting
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.import_export_repository import ImportExportRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.utils.datetime import utc_now


class AdminService:
    def __init__(self, db):
        self.db = db
        self.audit_repo = AuditRepository(db)
        self.import_export_repo = ImportExportRepository(db)
        self.user_repo = UserRepository(db)
        self.audit = AuditService(db)

    def list_users(self):
        return self.db.execute(select(User).order_by(User.created_at.desc())).scalars().all()

    def users_stmt(self):
        return select(User).order_by(User.created_at.desc())

    def list_settings(self):
        return self.db.execute(select(SystemSetting).order_by(SystemSetting.key.asc())).scalars().all()

    def list_audit_archives(self):
        return self.db.execute(select(AuditArchive).order_by(AuditArchive.archived_at.desc())).scalars().all()

    def list_audit_logs(self):
        return self.audit_repo.list_all()

    def audit_logs_stmt(self):
        return select(AuditLog).order_by(AuditLog.occurred_at.desc())

    def get_setting(self, key: str):
        value = self.db.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
        if not value:
            raise NotFoundError("Setting not found.")
        return value

    def upsert_settings(self, user, payload: dict):
        results = []
        for key, value in payload.items():
            if value is None:
                continue
            item = self.db.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
            if not item:
                item = SystemSetting(key=key, value_json={"value": value}, updated_by=user.username, updated_at=utc_now())
            else:
                item.value_json = {"value": value}
                item.updated_by = user.username
                item.updated_at = utc_now()
            self.db.add(item)
            results.append(item)
        self.audit.log(actor_user_id=user.id, action_type="settings_update", entity_type="system_settings", entity_id="bulk", metadata=payload)
        self.db.commit()
        return results
