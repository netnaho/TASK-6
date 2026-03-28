import json
import logging
import re
import sys
from contextvars import ContextVar


request_id_context: ContextVar[str] = ContextVar("request_id", default="")
SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "jwt_secret_key",
    "captcha_secret",
    "encryption_key",
}
BUILTIN_LOG_RECORD_KEYS = set(logging.makeLogRecord({}).__dict__.keys())


def redact_value(value):
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact_value(item)) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)(password|token|secret|encryption_key|jwt_secret_key|captcha_secret)\s*[=:]\s*[^\s,]+", r"\1=[REDACTED]", value)
        value = re.sub(r"Bearer\s+[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*", "Bearer [REDACTED]", value)
        return value
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": redact_value(record.getMessage()),
            "request_id": request_id_context.get(),
        }
        extra = {key: value for key, value in record.__dict__.items() if key not in BUILTIN_LOG_RECORD_KEYS}
        if extra:
            payload["context"] = redact_value(extra)
        if record.exc_info:
            payload["exception"] = redact_value(self.formatException(record.exc_info))
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
