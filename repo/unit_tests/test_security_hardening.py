import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.core.config import DEFAULT_CAPTCHA_SECRET, DEFAULT_ENCRYPTION_KEY, DEFAULT_JWT_SECRET, Settings
from app.core.logging import JsonFormatter
from app.main import app


def test_production_settings_reject_default_cryptographic_material():
    with pytest.raises(RuntimeError):
        Settings(environment="production", jwt_secret_key=DEFAULT_JWT_SECRET, captcha_secret=DEFAULT_CAPTCHA_SECRET, encryption_key=DEFAULT_ENCRYPTION_KEY)


def test_dev_settings_allow_default_cryptographic_material():
    settings = Settings(environment="dev", jwt_secret_key=DEFAULT_JWT_SECRET, captcha_secret=DEFAULT_CAPTCHA_SECRET, encryption_key=DEFAULT_ENCRYPTION_KEY)
    assert settings.environment == "dev"


def test_structured_logs_redact_sensitive_values():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="security",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="login failed password=SuperSecret#2026 token=eyJhbGciOiJIUzI1NiJ9.payload.signature",
        args=(),
        exc_info=None,
    )
    record.password = "SuperSecret#2026"
    record.access_token = "eyJhbGciOiJIUzI1NiJ9.payload.signature"
    record.encryption_key = "my-encryption-key"
    output = formatter.format(record)
    assert "SuperSecret#2026" not in output
    assert "payload.signature" not in output
    assert "my-encryption-key" not in output
    payload = json.loads(output)
    assert payload["context"]["password"] == "[REDACTED]"


def test_notification_mark_read_returns_404_for_missing_notification():
    client = TestClient(app)
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"})
    token = login.json()["data"]["access_token"]
    response = client.post("/api/v1/notifications/00000000-0000-0000-0000-000000000000/read", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
