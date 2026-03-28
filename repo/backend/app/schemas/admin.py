from pydantic import BaseModel


class SettingsUpdateRequest(BaseModel):
    enable_local_captcha: bool | None = None
    default_download_expiry_hours: int | None = None
    notifications_retention_days: int | None = None
    review_due_hours: int | None = None
