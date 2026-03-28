from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=255)
    password: str
    email_optional: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_challenge_token: str | None = None
    captcha_answer: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class CompleteForcedPasswordChangeRequest(BaseModel):
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_in_minutes: int
    refresh_expires_in_days: int
    force_password_change: bool = False


class CaptchaResponse(BaseModel):
    prompt: str
    challenge_token: str
