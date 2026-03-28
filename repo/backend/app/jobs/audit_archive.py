import json
from datetime import timedelta

from sqlalchemy import select

from app.core.config import get_settings
from app.models.audit import AuditArchive, AuditLog
from app.models.scheduler import SchedulerJobRun
from app.storage.file_manager import FileManager
from app.utils.datetime import utc_now


def archive_old_audit_logs(db):
    settings = get_settings()
    job = SchedulerJobRun(job_name="monthly_audit_archive", started_at=utc_now(), status="running", details_json={})
    db.add(job)
    db.flush()

    if not settings.audit_archive_enabled:
        job.finished_at = utc_now()
        job.status = "success"
        job.details_json = {"message": "Audit archiving disabled"}
        db.add(job)
        db.commit()
        return

    cutoff = utc_now() - timedelta(days=365 * settings.audit_retention_years)
    logs = db.execute(
        select(AuditLog)
        .where(AuditLog.occurred_at < cutoff, AuditLog.archived_at.is_(None))
        .order_by(AuditLog.occurred_at.asc())
    ).scalars().all()

    if not logs:
        job.finished_at = utc_now()
        job.status = "success"
        job.details_json = {"record_count": 0}
        db.add(job)
        db.commit()
        return

    lines = []
    archived_at = utc_now()
    for log in logs:
        payload = {
            "id": str(log.id),
            "occurred_at": log.occurred_at.isoformat(),
            "actor_user_id": str(log.actor_user_id) if log.actor_user_id else None,
            "action_type": log.action_type,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "ip_address": log.ip_address,
            "request_id": log.request_id,
            "metadata_json": log.metadata_json,
            "previous_hash": log.previous_hash,
            "entry_hash": log.entry_hash,
        }
        lines.append(json.dumps(payload, separators=(",", ":")))
        log.archived_at = archived_at
        db.add(log)

    content = ("\n".join(lines) + "\n").encode()
    filename = f"audit-{logs[0].occurred_at.date()}-{logs[-1].occurred_at.date()}.{settings.audit_archive_format}"
    file_path, _, checksum = FileManager().write_bytes("archives", filename, content)
    db.add(
        AuditArchive(
            archived_at=archived_at,
            record_count=len(logs),
            date_range_start=logs[0].occurred_at,
            date_range_end=logs[-1].occurred_at,
            file_path=file_path,
            checksum_sha256=checksum,
        )
    )

    job.finished_at = utc_now()
    job.status = "success"
    job.details_json = {"record_count": len(logs), "file_path": file_path, "checksum_sha256": checksum}
    db.add(job)
    db.commit()
