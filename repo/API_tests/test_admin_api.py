from API_tests.conftest import login_headers


def test_admin_disable_and_reset(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(user for user in users if user["username"] == "participant_demo")
    disabled = client.patch(f"/api/v1/admin/users/{participant['id']}", json={"status": "disabled", "is_active": False}, headers=admin_headers)
    assert disabled.status_code == 200
    denied_login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"})
    assert denied_login.status_code == 403
    enabled = client.patch(f"/api/v1/admin/users/{participant['id']}", json={"status": "active", "is_active": True}, headers=admin_headers)
    assert enabled.status_code == 200
    reset = client.post(f"/api/v1/admin/users/{participant['id']}/reset-password", json={"new_password": "ResetPass#2026"}, headers=admin_headers)
    assert reset.status_code == 200
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "ResetPass#2026"})
    assert login.status_code == 200
    assert login.json()["data"]["force_password_change"] is True


def test_admin_user_create_is_audit_logged_with_actor(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    created = client.post(
        "/api/v1/admin/users",
        json={"username": "audited_admin_create", "full_name": "Audited Create", "password": "AuditedCreate#2026", "role": "reviewer", "email_optional": "audited_create@example.local"},
        headers=admin_headers,
    )
    assert created.status_code == 200

    me = client.get("/api/v1/auth/me", headers=admin_headers)
    admin_id = me.json()["data"]["id"]
    audit = client.get("/api/v1/audit?page=1&page_size=200", headers=admin_headers)
    assert audit.status_code == 200
    assert any(item["action_type"] == "admin_user_create" and item["actor_user_id"] == admin_id for item in audit.json()["data"])


def test_admin_password_reset_audit_uses_admin_as_actor(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(user for user in users if user["username"] == "participant_demo")

    reset = client.post(
        f"/api/v1/admin/users/{participant['id']}/reset-password",
        json={"new_password": "ResetAudit#2026"},
        headers=admin_headers,
    )
    assert reset.status_code == 200

    me = client.get("/api/v1/auth/me", headers=admin_headers)
    admin_id = me.json()["data"]["id"]
    admin_username = me.json()["data"]["username"]

    audit = client.get("/api/v1/audit?page=1&page_size=200", headers=admin_headers)
    assert audit.status_code == 200
    reset_events = [
        item
        for item in audit.json()["data"]
        if item["action_type"] == "admin_password_reset"
        and item["entity_type"] == "user"
        and item["entity_id"] == participant["id"]
        and item["metadata_json"].get("forced") is True
    ]
    assert reset_events
    event = reset_events[0]
    assert event["actor_user_id"] == admin_id
    assert event["action_type"] == "admin_password_reset"
    assert event["entity_id"] == participant["id"]
    assert event["metadata_json"].get("target_user_id") == participant["id"]
    assert event["metadata_json"].get("admin_initiated") is True
    assert event["metadata_json"].get("admin_user_id") == admin_id
    assert event["metadata_json"].get("admin_username") == admin_username
