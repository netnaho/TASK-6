from fastapi import APIRouter, Depends, Request

from app.api.deps import DBSession, get_current_user, get_current_user_allow_force_change
from app.core.config import get_settings
from app.core.responses import success_response
from app.schemas.auth import CaptchaResponse, ChangePasswordRequest, CompleteForcedPasswordChangeRequest, LoginRequest, RefreshRequest, RegisterRequest
from app.security.captcha import create_captcha_challenge
from app.security.tokens import hash_refresh_token
from app.services.auth_service import AuthService
from app.utils.datetime import utc_now

router = APIRouter()


@router.post("/register")
def register(payload: RegisterRequest, db: DBSession):
    user = AuthService(db).register_participant(**payload.model_dump())
    return success_response({"id": str(user.id), "username": user.username}, "Registration successful")


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: DBSession):
    tokens = AuthService(db).login(**payload.model_dump(), user_agent=request.headers.get("user-agent"))
    return success_response(tokens, "Login successful")


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: DBSession):
    return success_response(AuthService(db).refresh(payload.refresh_token), "Token refreshed")


@router.post("/logout")
def logout(payload: RefreshRequest, db: DBSession, user=Depends(get_current_user_allow_force_change)):
    token = AuthService(db).repo.get_refresh_token(hash_refresh_token(payload.refresh_token))
    if token:
        token.revoked_at = utc_now()
        db.add(token)
        db.commit()
    return success_response(message="Logged out")


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: DBSession, user=Depends(get_current_user)):
    AuthService(db).change_password(user, payload.current_password, payload.new_password)
    return success_response(message="Password changed")


@router.post("/complete-forced-password-change")
def complete_forced(payload: CompleteForcedPasswordChangeRequest, db: DBSession, user=Depends(get_current_user_allow_force_change)):
    AuthService(db).complete_forced_password_change(user, payload.new_password)
    return success_response(message="Forced password change completed")


@router.get("/me")
def me(user=Depends(get_current_user_allow_force_change)):
    return success_response({
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
        "force_password_change": user.force_password_change,
    })


@router.get("/captcha/challenge")
def captcha():
    if not get_settings().enable_local_captcha:
        return success_response({"enabled": False})
    return success_response(create_captcha_challenge())
