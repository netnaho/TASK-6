import base64
import hashlib
import hmac
import json
import random

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.utils.datetime import add_minutes, utc_now


def create_captcha_challenge() -> dict:
    settings = get_settings()
    left = random.randint(1, 9)
    right = random.randint(1, 9)
    answer = str(left + right)
    payload = {"a": answer, "exp": int(add_minutes(settings.captcha_expire_minutes).timestamp())}
    raw = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(settings.captcha_secret.encode(), raw, hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(raw).decode() + "." + signature
    return {"prompt": f"What is {left} + {right}?", "challenge_token": token}


def verify_captcha(challenge_token: str, answer: str) -> None:
    settings = get_settings()
    try:
        encoded, signature = challenge_token.split(".", 1)
        raw = base64.urlsafe_b64decode(encoded.encode())
        expected = hmac.new(settings.captcha_secret.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise ValidationError("Invalid CAPTCHA challenge.", field="captcha")
        payload = json.loads(raw.decode())
        if int(payload["exp"]) < int(utc_now().timestamp()):
            raise ValidationError("CAPTCHA challenge expired.", field="captcha")
        if str(payload["a"]).strip() != str(answer).strip():
            raise ValidationError("Incorrect CAPTCHA answer.", field="captcha")
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError("Invalid CAPTCHA challenge.", field="captcha") from exc
