from app.models.notification import Notification
from app.models.scheduler import SchedulerJobRun
from app.models.settings import SystemSetting
from app.core.constants import NotificationSeverity, NotificationType
from app.repositories.user_repository import UserRepository
from app.jobs.notification_cleanup import cleanup_old_notifications
from app.services.notification_service import NotificationService
from app.utils.datetime import add_days, utc_now


def test_mandatory_alerts_cannot_be_muted(db_session):
    repo = UserRepository(db_session)
    participant = repo.get_by_username("participant_demo")
    prefs = repo.get_preferences(participant.id)
    prefs.status_changes_enabled = False
    db_session.add(prefs)
    db_session.commit()
    service = NotificationService(db_session)
    muted = service.create(user_id=participant.id, notification_type=NotificationType.STATUS_CHANGE, severity=NotificationSeverity.INFO, title="Status", message="status")
    required = service.create(user_id=participant.id, notification_type=NotificationType.MANDATORY_COMPLIANCE_ALERT, severity=NotificationSeverity.CRITICAL, title="Critical", message="must read")
    assert muted.is_muted_snapshot is True
    assert required.is_muted_snapshot is False


def test_notification_cleanup_uses_runtime_retention_setting(db_session):
    repo = UserRepository(db_session)
    participant = repo.get_by_username("participant_demo")
    setting = db_session.query(SystemSetting).filter(SystemSetting.key == "notifications_retention_days").one()
    setting.value_json = {"value": 1}
    setting.updated_by = "tester"
    setting.updated_at = utc_now()
    db_session.add(setting)
    stale = Notification(
        user_id=participant.id,
        type=NotificationType.STATUS_CHANGE,
        severity=NotificationSeverity.INFO,
        title="Stale",
        message="stale",
        is_muted_snapshot=False,
        created_at=add_days(-2),
        updated_at=add_days(-2),
    )
    fresh = Notification(
        user_id=participant.id,
        type=NotificationType.STATUS_CHANGE,
        severity=NotificationSeverity.INFO,
        title="Fresh",
        message="fresh",
        is_muted_snapshot=False,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db_session.add_all([stale, fresh])
    db_session.commit()

    cleanup_old_notifications(db_session)

    titles = {item.title for item in db_session.query(Notification).all()}
    assert "Stale" not in titles
    assert "Fresh" in titles
    job = db_session.query(SchedulerJobRun).filter(SchedulerJobRun.job_name == "cleanup_old_notifications").one()
    assert job.details_json["deleted_count"] >= 1
