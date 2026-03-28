"""add_created_at_to_version_tables

Revision ID: 27c0be069d2c
Revises: 0002_audit_archives
Create Date: 2026-03-28 08:04:39.843783
"""
from alembic import op
import sqlalchemy as sa



revision = '27c0be069d2c'
down_revision = '0002_audit_archives'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'nutrition_plan_versions',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        'nutrition_plan_versions',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        'participant_profile_versions',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        'participant_profile_versions',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        'package_versions',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        'package_versions',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('package_versions', 'updated_at')
    op.drop_column('package_versions', 'created_at')
    op.drop_column('participant_profile_versions', 'updated_at')
    op.drop_column('participant_profile_versions', 'created_at')
    op.drop_column('nutrition_plan_versions', 'updated_at')
    op.drop_column('nutrition_plan_versions', 'created_at')
