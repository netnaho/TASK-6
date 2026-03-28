import pytest
from sqlalchemy import text

from API_tests.conftest import login_headers
from app.services.audit_service import AuditService


def test_audit_log_query(client):
    headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    response = client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1


def test_audit_logs_are_immutable_except_archived_at(db_session):
    AuditService(db_session).log(
        actor_user_id=None,
        action_type="immutability_probe",
        entity_type="audit",
        entity_id="probe",
        metadata={},
    )
    db_session.commit()
    audit_id = db_session.execute(text("SELECT id FROM audit_logs ORDER BY occurred_at DESC LIMIT 1")).scalar_one()

    with pytest.raises(Exception):
        db_session.execute(text("UPDATE audit_logs SET action_type = 'tampered' WHERE id = :id"), {"id": audit_id})
        db_session.commit()
    db_session.rollback()

    with pytest.raises(Exception):
        db_session.execute(text("DELETE FROM audit_logs WHERE id = :id"), {"id": audit_id})
        db_session.commit()
    db_session.rollback()

    db_session.execute(text("UPDATE audit_logs SET archived_at = NOW() WHERE id = :id"), {"id": audit_id})
    db_session.commit()
    archived_at = db_session.execute(text("SELECT archived_at FROM audit_logs WHERE id = :id"), {"id": audit_id}).scalar_one()
    assert archived_at is not None
