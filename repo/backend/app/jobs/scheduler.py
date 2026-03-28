import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.jobs.audit_archive import archive_old_audit_logs
from app.jobs.notification_cleanup import cleanup_old_notifications
from app.jobs.reviewer_stats import refresh_reviewer_stats
from app.jobs.search_index import rebuild_search_index
from app.jobs.token_cleanup import cleanup_expired_download_tokens

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="UTC")


def _run_with_session(func):
    def wrapper():
        db = SessionLocal()
        try:
            func(db)
        except Exception:
            logger.exception("Scheduled job failed", extra={"job": func.__name__})
            db.rollback()
        finally:
            db.close()

    return wrapper


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(_run_with_session(rebuild_search_index), "cron", hour=2, minute=0, id="search-index")
    scheduler.add_job(_run_with_session(refresh_reviewer_stats), "cron", minute=0, id="reviewer-stats")
    scheduler.add_job(_run_with_session(cleanup_expired_download_tokens), "cron", minute="*/15", id="token-cleanup")
    scheduler.add_job(_run_with_session(cleanup_old_notifications), "cron", hour=3, minute=0, id="notification-cleanup")
    scheduler.add_job(_run_with_session(archive_old_audit_logs), "cron", day=1, hour=4, minute=0, id="audit-archive")
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
