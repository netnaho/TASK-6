import pytest

from app.core.exceptions import AuthenticationError
from app.models.delivery import DeliveryFile, DownloadToken
from app.repositories.declaration_repository import DeclarationRepository
from app.repositories.user_repository import UserRepository
from app.security.tokens import hash_download_token
from app.services.delivery_service import DeliveryService
from app.storage.file_manager import FileManager
from app.utils.datetime import add_hours


def test_download_token_expiry_is_enforced(db_session):
    package = DeclarationRepository(db_session).list_for_user(UserRepository(db_session).get_by_username("participant_demo"))[0]
    participant = UserRepository(db_session).get_by_username("participant_demo")
    path, size, checksum = FileManager().write_bytes("deliveries", "sample.txt", b"sample")
    file = DeliveryFile(package_id=package.id, file_type="revision_note", display_name="sample.txt", storage_path=path, mime_type="text/plain", checksum_sha256=checksum, size_bytes=size, created_by="system")
    db_session.add(file)
    db_session.flush()
    token = DownloadToken(package_id=package.id, delivery_file_id=file.id, issued_to_user_id=participant.id, token_hash=hash_download_token("expired-token"), expires_at=add_hours(-1), issued_by="system", purpose="download")
    db_session.add(token)
    db_session.commit()
    with pytest.raises(AuthenticationError):
        DeliveryService(db_session).validate_download(participant, "expired-token")
