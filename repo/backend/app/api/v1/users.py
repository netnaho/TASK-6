from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.schemas.users import NotificationPreferencesUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me/preferences")
def get_preferences(db: DBSession, user=Depends(get_current_user)):
    prefs = UserService(db).repo.get_preferences(user.id)
    return success_response(prefs)


@router.patch("/me/preferences")
def update_preferences(payload: NotificationPreferencesUpdate, db: DBSession, user=Depends(get_current_user)):
    prefs = UserService(db).update_preferences(user.id, payload)
    return success_response(prefs, "Preferences updated")
