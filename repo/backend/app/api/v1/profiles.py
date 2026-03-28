from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.security.permissions import ensure_profile_owner
from app.schemas.profiles import ProfileRead, ProfileUpsertRequest, ProfileVersionRead
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("/me")
def get_my_profile(db: DBSession, user=Depends(require_roles(Role.PARTICIPANT, Role.ADMINISTRATOR))):
    profile = ProfileService(db).get_me(user.id)
    return success_response(ProfileRead.model_validate(profile))


@router.post("/me")
def create_profile(payload: ProfileUpsertRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    profile = ProfileService(db).upsert(user, payload)
    return success_response(ProfileRead.model_validate(profile), "Profile saved")


@router.put("/me")
def update_profile(payload: ProfileUpsertRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    profile = ProfileService(db).upsert(user, payload)
    return success_response(ProfileRead.model_validate(profile), "Profile updated")


@router.get("/me/history")
def profile_history(db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    versions = ProfileService(db).history(user.id)
    return success_response([ProfileVersionRead.model_validate(version) for version in versions])


@router.get("/me/history/{version_id}")
def profile_version(version_id: str, db: DBSession, user=Depends(get_current_user)):
    version = ProfileService(db).get_version(user, version_id)
    ensure_profile_owner(user, version.profile)
    return success_response(ProfileVersionRead.model_validate(version))
