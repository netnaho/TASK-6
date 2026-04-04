from fastapi import APIRouter, Depends

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import Role
from app.core.responses import success_response
from app.security.permissions import ensure_package_access
from app.schemas.declarations import CorrectionRequestCreate
from app.schemas.reviews import ReviewCompleteRequest
from app.services.declaration_service import DeclarationService
from app.utils.pagination import PaginationParams, paginate_query

router = APIRouter()


@router.get("/queue")
def reviewer_queue(db: DBSession, params: PaginationParams = Depends(), user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    service = DeclarationService(db)
    paginated = paginate_query(db, service.repo.queue_stmt_for_reviewer(user.id), params)
    return success_response(paginated.items, meta=paginated.meta)


@router.post("/{package_id}/request-correction")
def request_correction(package_id: str, payload: CorrectionRequestCreate, db: DBSession, user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    service = DeclarationService(db)
    package = service.get(package_id)
    ensure_package_access(user, package)
    correction = service.request_correction(user, package_id, payload)
    return success_response(correction, "Correction requested")


@router.get("/{package_id}/corrections")
def corrections(package_id: str, db: DBSession, user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    package = DeclarationService(db).get(package_id)
    ensure_package_access(user, package)
    return success_response(package.correction_requests)


@router.get("/{package_id}/context")
def review_context(package_id: str, db: DBSession, user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    service = DeclarationService(db)
    package = service.get(package_id)
    ensure_package_access(user, package)
    return success_response(service.get_review_context(package_id))


@router.post("/{package_id}/complete")
def complete_review(package_id: str, payload: ReviewCompleteRequest, db: DBSession, user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    service = DeclarationService(db)
    package = service.get(package_id)
    ensure_package_access(user, package)
    assignment = service.complete_review(user, package_id, payload.note)
    return success_response(assignment, "Review marked complete")
