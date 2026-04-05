from app.models.notification import Notification
from app.models.scheduler import SchedulerJobRun
from app.services.runtime_settings_service import RuntimeSettingsService
from app.utils.datetime import add_days, utc_now


def cleanup_old_notifications(db):
    runtime_settings = RuntimeSettingsService(db)
    job = SchedulerJobRun(job_name="cleanup_old_notifications", started_at=utc_now(), status="running", details_json={})
    db.add(job)
    db.flush()
    retention_value = runtime_settings.get("notifications_retention_days", 90)
    retention_days = int(retention_value) if isinstance(retention_value, (int, float, str)) and not isinstance(retention_value, bool) else 90
    cutoff = add_days(-retention_days)
    notifications = db.query(Notification).filter(Notification.created_at < cutoff).all()
    count = len(notifications)
    for notification in notifications:
        db.delete(notification)
    job.finished_at = utc_now()
    job.status = "success"
    job.details_json = {"deleted_count": count}
    db.add(job)
    db.commit()
