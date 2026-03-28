from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.security.permissions import ensure_plan_owner
from app.schemas.plans import PlanCreateRequest, PlanVersionRead
from app.services.plan_service import PlanService

router = APIRouter()


@router.get("")
def list_plans(db: DBSession, user=Depends(get_current_user)):
    return success_response(PlanService(db).list_for_user(user))


@router.post("")
def create_plan(payload: PlanCreateRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    return success_response(PlanService(db).create(user, payload), "Plan created")


@router.get("/{plan_id}")
def get_plan(plan_id: str, db: DBSession, user=Depends(get_current_user)):
    plan = PlanService(db).get(plan_id)
    ensure_plan_owner(user, plan)
    return success_response(plan)


@router.put("/{plan_id}")
def update_plan(plan_id: str, payload: PlanCreateRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    ensure_plan_owner(user, PlanService(db).get(plan_id))
    return success_response(PlanService(db).update(user, plan_id, payload), "Plan updated")


@router.get("/{plan_id}/versions")
def plan_versions(plan_id: str, db: DBSession, user=Depends(get_current_user)):
    versions = PlanService(db).versions(user, plan_id)
    return success_response([PlanVersionRead.model_validate(version) for version in versions])


@router.get("/versions/{version_id}")
def plan_version(version_id: str, db: DBSession, user=Depends(get_current_user)):
    version = PlanService(db).get_version(user, version_id)
    return success_response(PlanVersionRead.model_validate(version))
