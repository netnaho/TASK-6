"""migrate_profile_payloads_to_pgcrypto_only

Revision ID: 6f1a2c9d4e5b
Revises: 9d3e4a7c2b11
Create Date: 2026-03-28 12:40:00
"""

import base64
import json
import os

from alembic import op
import sqlalchemy as sa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


revision = "6f1a2c9d4e5b"
down_revision = "9d3e4a7c2b11"
branch_labels = None
depends_on = None


def _resolve_db_key() -> str:
    db_key = os.getenv("DB_ENCRYPTION_KEY") or os.getenv("ENCRYPTION_KEY")
    if not db_key:
        raise RuntimeError("DB_ENCRYPTION_KEY or ENCRYPTION_KEY must be set for pgcrypto migration.")
    return db_key


def _decrypt_legacy_payload(value: str) -> dict:
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        raise RuntimeError("ENCRYPTION_KEY must be set to migrate legacy AES-encrypted profile payloads.")
    raw = base64.urlsafe_b64decode(value.encode())
    nonce, ciphertext = raw[:12], raw[12:]
    plaintext = AESGCM(base64.urlsafe_b64decode(encryption_key)).decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())


def upgrade() -> None:
    bind = op.get_bind()
    db_key = _resolve_db_key()
    rows = bind.execute(
        sa.text(
            """
            SELECT id, pgp_sym_decrypt(dearmor(encrypted_payload), :db_key)::text AS decrypted_payload
            FROM participant_profiles
            WHERE encrypted_payload IS NOT NULL
              AND encrypted_payload <> ''
            """
        ),
        {"db_key": db_key},
    ).mappings()

    for row in rows:
        decrypted_payload = row["decrypted_payload"]
        try:
            json.loads(decrypted_payload)
            continue
        except json.JSONDecodeError:
            payload = _decrypt_legacy_payload(decrypted_payload)

        bind.execute(
            sa.text(
                """
                UPDATE participant_profiles
                SET encrypted_payload = armor(pgp_sym_encrypt(:payload, :db_key))
                WHERE id = :id
                """
            ),
            {"id": row["id"], "payload": json.dumps(payload), "db_key": db_key},
        )


def downgrade() -> None:
    pass
