from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import DBSession, get_current_user, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.core.responses import success_response
from app.security.permissions import ensure_package_access
from app.schemas.deliveries import AcceptanceRequest, DeliveryLinkRequest
from app.services.delivery_service import DeliveryService
from app.services.declaration_service import DeclarationService

router = APIRouter()


@router.get("/{package_id}")
def list_delivery_files(package_id: str, db: DBSession, user=Depends(get_current_user)):
    return success_response(DeliveryService(db).list_files(user, package_id))


@router.post("/{package_id}/files")
async def upload_delivery_file(package_id: str, file_type: str = Form(...), is_final: bool = Form(False), allowed_roles: list[str] | None = Form(None), upload: UploadFile = File(...), db=Depends(get_db), user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    file = await DeliveryService(db).upload_file(user, package_id, upload, file_type, is_final, allowed_roles)
    return success_response(file, "Delivery file uploaded")


@router.post("/{package_id}/links")
def create_delivery_link(package_id: str, payload: DeliveryLinkRequest, db: DBSession, user=Depends(require_roles(Role.REVIEWER, Role.ADMINISTRATOR))):
    result = DeliveryService(db).create_download_link(user, package_id, payload.delivery_file_id, payload.expires_in_hours, payload.purpose, payload.issued_to_user_id)
    return success_response(result, "Download link created")


@router.post("/{package_id}/bulk-download")
def bulk_download(package_id: str, db: DBSession, user=Depends(get_current_user)):
    payload = DeliveryService(db).generate_bulk_package(user, package_id)
    return success_response(payload, "Bulk package download prepared")


@router.post("/{package_id}/acceptance")
def accept_delivery(package_id: str, payload: AcceptanceRequest, db: DBSession, user=Depends(require_roles(Role.PARTICIPANT))):
    confirmation = DeliveryService(db).accept(user, package_id, payload.confirmation_note, payload.accepted_delivery_version)
    return success_response(confirmation, "Acceptance recorded")


@router.get("/{package_id}/acceptance")
def acceptance_history(package_id: str, db: DBSession, user=Depends(get_current_user)):
    package = DeclarationService(db).get(package_id)
    ensure_package_access(user, package)
    return success_response(DeliveryService(db).repo.list_acceptance(package_id))
