from app.core.constants import NotificationSeverity, NotificationType
from app.models.notification import Notification

from API_tests.conftest import login_headers


def create_declaration(client, headers):
    profile = client.get("/api/v1/profiles/me", headers=headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=headers).json()["data"][0]
    response = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile["id"], "plan_id": plan["id"]},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


def test_declarations_pagination(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    for _ in range(3):
        create_declaration(client, headers)
    response = client.get("/api/v1/declarations?page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total_pages"] > 1


def test_notifications_pagination(client, db_session):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    participant_id = client.get("/api/v1/auth/me", headers=headers).json()["data"]["id"]
    for index in range(3):
        db_session.add(
            Notification(
                user_id=participant_id,
                type=NotificationType.STATUS_CHANGE,
                severity=NotificationSeverity.INFO,
                title=f"Notice {index}",
                message="Paged notification",
                is_muted_snapshot=False,
            )
        )
    db_session.commit()
    response = client.get("/api/v1/notifications?page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total_pages"] > 1


def test_admin_users_pagination(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    client.post("/api/v1/admin/users", json={"username": "reviewer_extra", "full_name": "Reviewer Extra", "password": "ReviewerExtra#2026", "role": "reviewer"}, headers=admin_headers)
    response = client.get("/api/v1/admin/users?page=1&page_size=2", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total_pages"] > 1


def test_audit_pagination(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    client.post("/api/v1/auth/register", json={"username": "audit_one", "full_name": "Audit One", "password": "AuditPass#2026", "email_optional": "audit1@example.local"})
    client.post("/api/v1/auth/register", json={"username": "audit_two", "full_name": "Audit Two", "password": "AuditPass#2027", "email_optional": "audit2@example.local"})
    response = client.get("/api/v1/audit?page=1&page_size=2", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total_pages"] > 1


def test_reviewer_queue_pagination(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    ids = [create_declaration(client, participant_headers) for _ in range(3)]
    for package_id in ids:
        submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=participant_headers)
        assert submitted.status_code == 200
    response = client.get("/api/v1/reviews/queue?page=1&page_size=2", headers=reviewer_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total_pages"] > 1
