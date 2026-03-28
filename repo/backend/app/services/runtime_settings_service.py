from app.models.settings import SystemSetting


class RuntimeSettingsService:
    def __init__(self, db):
        self.db = db

    def get(self, key: str, default=None):
        setting = self.db.query(SystemSetting).filter(SystemSetting.key == key).one_or_none()
        if not setting:
            return default
        value = setting.value_json.get("value") if isinstance(setting.value_json, dict) else None
        return default if value is None else value
