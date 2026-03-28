from sqlalchemy import select

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    def latest(self):
        return self.scalar_one_or_none(select(AuditLog).order_by(AuditLog.occurred_at.desc()).limit(1))

    def list_all(self):
        return self.list_scalars(select(AuditLog).order_by(AuditLog.occurred_at.desc()))
