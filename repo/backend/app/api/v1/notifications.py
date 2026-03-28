from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user
from app.core.constants import NotificationType
from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.responses import success_response
from app.repositories.notification_repository import NotificationRepository
from app.schemas.users import NotificationPreferencesUpdate
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter()


@router.get("")
def list_notifications(db: DBSession, params: PaginationParams = Depends(), user=Depends(get_current_user)):
    repo = NotificationRepository(db)
    paginated = paginate_query(db, repo.stmt_for_user(user.id), params)
    return success_response(paginated.items, meta=paginated.meta)


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, db: DBSession, user=Depends(get_current_user)):
    notification = NotificationRepository(db).get(notification_id)
    if not notification:
        raise NotFoundError("Notification not found.")
    if str(notification.user_id) != str(user.id):
        raise AuthorizationError("You do not have permission to modify this notification.")
    notification.is_read = True
    db.add(notification)
    db.commit()
    return success_response(notification, "Notification marked read")


@router.post("/read-all")
def mark_all_read(db: DBSession, user=Depends(get_current_user)):
    notifications = NotificationRepository(db).list_for_user(user.id)
    for notification in notifications:
        notification.is_read = True
        db.add(notification)
    db.commit()
    return success_response(message="Notifications marked read")


@router.patch("/preferences")
def update_notification_preferences(payload: NotificationPreferencesUpdate, db: DBSession, user=Depends(get_current_user)):
    prefs = UserService(db).update_preferences(user.id, payload)
    return success_response(prefs, "Notification preferences updated")


@router.get("/preferences")
def get_preferences(db: DBSession, user=Depends(get_current_user)):
    return success_response(NotificationService(db).get_preferences(user.id))


@router.get("/mandatory-alerts")
def mandatory_alerts(db: DBSession, user=Depends(get_current_user)):
    alerts = [item for item in NotificationRepository(db).list_for_user(user.id) if item.type == NotificationType.MANDATORY_COMPLIANCE_ALERT]
    return success_response(alerts)
