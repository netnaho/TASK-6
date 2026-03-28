"""enable_pgcrypto_db_encryption

Revision ID: b39f8e2d1c4a
Revises: 27c0be069d2c
Create Date: 2026-03-28 09:05:00
"""

import os

from alembic import op
import sqlalchemy as sa


revision = "b39f8e2d1c4a"
down_revision = "27c0be069d2c"
branch_labels = None
depends_on = None


def _resolve_db_key() -> str:
    db_key = os.getenv("DB_ENCRYPTION_KEY") or os.getenv("ENCRYPTION_KEY")
    if not db_key:
        raise RuntimeError("DB_ENCRYPTION_KEY or ENCRYPTION_KEY must be set for pgcrypto migration.")
    return db_key


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    bind = op.get_bind()
    db_key = _resolve_db_key()
    bind.execute(
        sa.text(
            """
            UPDATE participant_profiles
            SET encrypted_payload = armor(pgp_sym_encrypt(encrypted_payload, :db_key))
            WHERE encrypted_payload IS NOT NULL
              AND encrypted_payload <> ''
            """
        ),
        {"db_key": db_key},
    )


def downgrade() -> None:
    bind = op.get_bind()
    db_key = _resolve_db_key()
    bind.execute(
        sa.text(
            """
            UPDATE participant_profiles
            SET encrypted_payload = pgp_sym_decrypt(dearmor(encrypted_payload), :db_key)::text
            WHERE encrypted_payload IS NOT NULL
              AND encrypted_payload <> ''
            """
        ),
        {"db_key": db_key},
    )
