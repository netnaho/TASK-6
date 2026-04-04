import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import Text, cast, func, literal, text
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.types import TypeDecorator

from app.core.config import get_settings


class EncryptionService:
    def __init__(self) -> None:
        settings = get_settings()
        self.key = base64.urlsafe_b64decode(settings.encryption_key)
        self.db_encryption_enabled = settings.db_encryption_enabled
        self.db_key = settings.effective_db_encryption_key

    def encrypt_dict(self, payload: dict) -> str:
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, json.dumps(payload).encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt_dict(self, encrypted_payload: str | None) -> dict:
        if not encrypted_payload:
            return {}
        aesgcm = AESGCM(self.key)
        raw = base64.urlsafe_b64decode(encrypted_payload.encode())
        nonce, ciphertext = raw[:12], raw[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode())

    def ensure_pgcrypto_extension(self, db) -> None:
        if not self.db_encryption_enabled:
            return
        db.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    def db_encrypt_expression(self, value: ColumnElement):
        if not self.db_encryption_enabled:
            return value
        return func.armor(func.pgp_sym_encrypt(cast(value, Text), cast(literal(self.db_key), Text)))

    def db_decrypt_expression(self, value: ColumnElement):
        if not self.db_encryption_enabled:
            return value
        return func.pgp_sym_decrypt(func.dearmor(value), cast(literal(self.db_key), Text)).cast(Text)


class PgcryptoEncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self) -> None:
        super().__init__()
        self.encryption = EncryptionService()

    def bind_expression(self, bindvalue):
        return self.encryption.db_encrypt_expression(bindvalue)

    def column_expression(self, column):
        return self.encryption.db_decrypt_expression(column)


class PgcryptoEncryptedJSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self) -> None:
        super().__init__()
        self.encryption = EncryptionService()

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

    def bind_expression(self, bindvalue):
        return self.encryption.db_encrypt_expression(bindvalue)

    def column_expression(self, column):
        return self.encryption.db_decrypt_expression(column)
