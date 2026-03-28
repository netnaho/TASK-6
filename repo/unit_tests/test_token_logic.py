from app.repositories.user_repository import UserRepository
from app.security.tokens import decode_access_token, decode_refresh_token
from app.services.auth_service import AuthService


def test_access_and_refresh_tokens_are_issued_and_rotated(db_session):
    service = AuthService(db_session)
    login = service.login("participant_demo", "Participant#2026")
    access_payload = decode_access_token(login["access_token"])
    refresh_payload = decode_refresh_token(login["refresh_token"])
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    rotated = service.refresh(login["refresh_token"])
    assert rotated["refresh_token"] != login["refresh_token"]
