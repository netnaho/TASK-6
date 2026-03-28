from app.core.config import get_settings
from app.models.notification import Notification
from app.models.scheduler import SchedulerJobRun
from app.utils.datetime import add_days, utc_now


def cleanup_old_notifications(db):
    settings = get_settings()
    job = SchedulerJobRun(job_name="cleanup_old_notifications", started_at=utc_now(), status="running", details_json={})
    db.add(job)
    db.flush()
    cutoff = add_days(-settings.notifications_retention_days)
    notifications = db.query(Notification).filter(Notification.created_at < cutoff).all()
    count = len(notifications)
    for notification in notifications:
        db.delete(notification)
    job.finished_at = utc_now()
    job.status = "success"
    job.details_json = {"deleted_count": count}
    db.add(job)
    db.commit()
