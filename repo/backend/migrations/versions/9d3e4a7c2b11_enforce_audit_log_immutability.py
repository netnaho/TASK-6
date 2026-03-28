"""enforce_audit_log_immutability

Revision ID: 9d3e4a7c2b11
Revises: b39f8e2d1c4a
Create Date: 2026-03-28 10:15:00
"""

from alembic import op


revision = "9d3e4a7c2b11"
down_revision = "b39f8e2d1c4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_audit_log_delete()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs is append-only and cannot be deleted';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION restrict_audit_log_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF (to_jsonb(NEW) - 'archived_at') IS DISTINCT FROM (to_jsonb(OLD) - 'archived_at') THEN
                RAISE EXCEPTION 'audit_logs is immutable; only archived_at may be updated';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_prevent_audit_log_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_log_delete();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_restrict_audit_log_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION restrict_audit_log_update();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_restrict_audit_log_update ON audit_logs")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_audit_log_delete ON audit_logs")
    op.execute("DROP FUNCTION IF EXISTS restrict_audit_log_update()")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_delete()")
