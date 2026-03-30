from API_tests.conftest import login_headers


def test_notifications_and_mute_settings(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    notifications = client.get("/api/v1/notifications", headers=headers)
    assert notifications.status_code == 200
    prefs = client.patch("/api/v1/notifications/preferences", json={"status_changes_enabled": False}, headers=headers)
    assert prefs.status_code == 200
    all_read = client.post("/api/v1/notifications/read-all", headers=headers)
    assert all_read.status_code == 200


def test_users_preferences_endpoint_uses_typed_payload_model(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")

    updated = client.patch(
        "/api/v1/users/me/preferences",
        json={"mentions_enabled": False},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["mentions_enabled"] is False

    fetched = client.get("/api/v1/users/me/preferences", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["mentions_enabled"] is False


def test_notification_preferences_reject_unexpected_keys_and_user_tampering(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")

    bad_key = client.patch(
        "/api/v1/notifications/preferences",
        json={"status_changes_enabled": False, "debug_mode": True},
        headers=headers,
    )
    assert bad_key.status_code == 422
    assert "Extra inputs are not permitted" in bad_key.text

    tamper = client.patch(
        "/api/v1/notifications/preferences",
        json={"status_changes_enabled": False, "user_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )
    assert tamper.status_code == 422
    assert "Extra inputs are not permitted" in tamper.text

    preferences = client.get("/api/v1/notifications/preferences", headers=headers)
    assert preferences.status_code == 200
    assert preferences.json()["data"]["status_changes_enabled"] is True


def test_notification_mark_read_returns_not_found_for_missing_notification(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    response = client.post("/api/v1/notifications/00000000-0000-0000-0000-000000000000/read", headers=headers)
    assert response.status_code == 404


def test_mentions_and_deadline_warning_notifications_are_produced(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={
            "overall_message": "Please coordinate with @admin_demo before resubmitting.",
            "sections_json": [{"section": "plan", "issue": "Clarify target for @admin_demo"}],
            "response_due_hours": 12,
        },
        headers=reviewer_headers,
    )
    assert correction.status_code == 200

    participant_notifications = client.get("/api/v1/notifications", headers=participant_headers)
    assert participant_notifications.status_code == 200
    participant_types = [item["type"] for item in participant_notifications.json()["data"]]
    assert "deadline_warning" in participant_types

    admin_notifications = client.get("/api/v1/notifications", headers=admin_headers)
    assert admin_notifications.status_code == 200
    mention_notifications = [item for item in admin_notifications.json()["data"] if item["type"] == "mention"]
    assert mention_notifications


def test_submission_can_create_reviewer_deadline_warning_for_short_sla(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")

    settings_update = client.put(
        "/api/v1/admin/settings",
        json={"review_due_hours": 12},
        headers=admin_headers,
    )
    assert settings_update.status_code == 200

    profile = client.get("/api/v1/profiles/me", headers=participant_headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=participant_headers).json()["data"][0]
    package = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile["id"], "plan_id": plan["id"]},
        headers=participant_headers,
    ).json()["data"]

    submitted = client.post(f"/api/v1/declarations/{package['id']}/submit", json={}, headers=participant_headers)
    assert submitted.status_code == 200

    reviewer_notifications = client.get("/api/v1/notifications", headers=reviewer_headers)
    assert reviewer_notifications.status_code == 200
    deadline_notifications = [item for item in reviewer_notifications.json()["data"] if item["type"] == "deadline_warning"]
    assert deadline_notifications
