from app.core.constants import NotificationSeverity, NotificationType
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService


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
