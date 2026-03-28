from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.deps import DBSession, get_current_user
from app.services.delivery_service import DeliveryService
from app.storage.file_manager import FileManager

router = APIRouter()


@router.get("/{token}")
def download(token: str, db: DBSession, user=Depends(get_current_user)):
    file = DeliveryService(db).validate_download(user, token)
    content = FileManager().read_bytes(file.storage_path)
    return Response(content=content, media_type=file.mime_type, headers={"Content-Disposition": f'attachment; filename="{file.display_name}"'})
