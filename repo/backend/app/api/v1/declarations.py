from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import DeclarationState, Role
from app.core.responses import success_response
from app.security.permissions import ensure_package_access, ensure_package_owner
from app.schemas.declarations import CorrectionAcknowledgeRequest, CorrectionResubmitRequest, DeclarationCreateRequest, PackageVersionRead, StateChangeRequest
from app.services.declaration_service import DeclarationService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter()


@router.get("")
def list_declarations(db: DBSession, params: PaginationParams = Depends(), user=Depends(get_current_user)):
    service = DeclarationService(db)
    paginated = paginate_query(db, service.repo.stmt_for_user(user), params)
    return success_response(paginated.items, meta=paginated.meta)


@router.post("")
def create_declaration(payload: DeclarationCreateRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    package = DeclarationService(db).create(user, payload.profile_id, payload.plan_id)
    return success_response(package, "Declaration draft created")


@router.get("/{package_id}")
def get_declaration(package_id: str, db: DBSession, user=Depends(get_current_user)):
    package = DeclarationService(db).get(package_id)
    ensure_package_access(user, package)
    return success_response(package)


@router.post("/{package_id}/submit")
def submit_declaration(package_id: str, payload: StateChangeRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    ensure_package_owner(user, DeclarationService(db).get(package_id))
    package = DeclarationService(db).transition(user, package_id, DeclarationState.SUBMITTED, payload.reason_code, payload.reason_text)
    return success_response(package, "Declaration submitted")


@router.post("/{package_id}/withdraw")
def withdraw_declaration(package_id: str, payload: StateChangeRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    ensure_package_owner(user, DeclarationService(db).get(package_id))
    package = DeclarationService(db).transition(user, package_id, DeclarationState.WITHDRAWN, payload.reason_code, payload.reason_text)
    return success_response(package, "Declaration withdrawn")


@router.post("/{package_id}/reopen")
def reopen_declaration(package_id: str, payload: StateChangeRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    ensure_package_owner(user, DeclarationService(db).get(package_id))
    package = DeclarationService(db).transition(user, package_id, DeclarationState.DRAFT, payload.reason_code, payload.reason_text)
    return success_response(package, "Declaration reopened")


@router.post("/{package_id}/void")
def void_declaration(package_id: str, payload: StateChangeRequest, db: DBSession, user=Depends(require_roles(Role.ADMINISTRATOR))):
    package = DeclarationService(db).transition(user, package_id, DeclarationState.VOIDED, payload.reason_code, payload.reason_text)
    return success_response(package, "Declaration voided")


@router.get("/{package_id}/history")
def declaration_history(package_id: str, db: DBSession, user=Depends(get_current_user)):
    package = DeclarationService(db).get(package_id)
    ensure_package_access(user, package)
    return success_response({
        "versions": [PackageVersionRead.model_validate(version) for version in package.versions],
        "state_history": package.state_history,
    })


@router.get("/{package_id}/corrections")
def declaration_corrections(package_id: str, db: DBSession, user=Depends(get_current_user)):
    package = DeclarationService(db).get(package_id)
    ensure_package_access(user, package)
    return success_response(package.correction_requests)


@router.post("/{package_id}/corrections/{correction_id}/acknowledge")
def acknowledge_correction(package_id: str, correction_id: str, payload: CorrectionAcknowledgeRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    correction = DeclarationService(db).acknowledge_correction(user, package_id, correction_id)
    return success_response(correction, "Correction acknowledged")


@router.post("/{package_id}/corrections/{correction_id}/resubmit")
def resubmit_correction(package_id: str, correction_id: str, payload: CorrectionResubmitRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    package = DeclarationService(db).resubmit_correction(user, package_id, correction_id, payload.reason_text)
    return success_response(package, "Correction resubmitted")
