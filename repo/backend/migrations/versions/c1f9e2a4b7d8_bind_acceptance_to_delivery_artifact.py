"""bind acceptance to delivery artifact

Revision ID: c1f9e2a4b7d8
Revises: 6f1a2c9d4e5b
Create Date: 2026-04-05 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c1f9e2a4b7d8"
down_revision = "6f1a2c9d4e5b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "acceptance_confirmations",
        sa.Column("delivery_file_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_acceptance_confirmations_delivery_file_id"), "acceptance_confirmations", ["delivery_file_id"], unique=False)
    op.create_foreign_key(
        "fk_acceptance_confirmations_delivery_file_id",
        "acceptance_confirmations",
        "delivery_files",
        ["delivery_file_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_acceptance_confirmations_delivery_file_id", "acceptance_confirmations", type_="foreignkey")
    op.drop_index(op.f("ix_acceptance_confirmations_delivery_file_id"), table_name="acceptance_confirmations")
    op.drop_column("acceptance_confirmations", "delivery_file_id")
