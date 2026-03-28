from fastapi import APIRouter, Depends

from app.api.deps import DBSession, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.schemas.admin import SettingsUpdateRequest
from app.schemas.users import AdminPasswordResetRequest, AdminUserCreate, AdminUserUpdate
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter()


@router.get("/users")
def list_users(db: DBSession, params: PaginationParams = Depends(), user=Depends(require_roles(Role.ADMINISTRATOR))):
    service = AdminService(db)
    paginated = paginate_query(db, service.users_stmt(), params)
    return success_response(paginated.items, meta=paginated.meta)


@router.post("/users")
def create_user(payload: AdminUserCreate, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(UserService(db).create_user(user, payload), "User created")


@router.patch("/users/{user_id}")
def update_user(user_id: str, payload: AdminUserUpdate, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(UserService(db).update_user(user, user_id, payload), "User updated")


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: str, payload: AdminPasswordResetRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    target = UserService(db).get_user(user_id)
    AuthService(db).admin_reset_password(target, payload.new_password, admin_user=user)
    return success_response(message="Password reset completed")


@router.get("/settings")
def list_settings(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(AdminService(db).list_settings())


@router.get("/audit-archives")
def list_audit_archives(db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(AdminService(db).list_audit_archives())


@router.put("/settings")
def update_settings(payload: SettingsUpdateRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    return success_response(AdminService(db).upsert_settings(user, payload.model_dump()), "Settings updated")
