from app.models.audit import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.security.tokens import compute_audit_hash
from app.utils.datetime import utc_now


class AuditService:
    def __init__(self, db):
        self.db = db
        self.repo = AuditRepository(db)

    def log(self, *, actor_user_id, action_type: str, entity_type: str, entity_id: str, metadata: dict, ip_address: str | None = None, request_id: str | None = None):
        previous = self.repo.latest()
        payload = {
            "occurred_at": utc_now().isoformat(),
            "actor_user_id": str(actor_user_id) if actor_user_id else None,
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata,
        }
        audit = AuditLog(
            occurred_at=utc_now(),
            actor_user_id=actor_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            request_id=request_id,
            metadata_json=metadata,
            previous_hash=previous.entry_hash if previous else None,
            entry_hash=compute_audit_hash(previous.entry_hash if previous else None, payload),
        )
        self.db.add(audit)
        return audit
