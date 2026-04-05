from io import BytesIO

from API_tests.conftest import login_headers


def register_participant(client, username: str, password: str = "ParticipantTwo#2026"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "full_name": f"{username} User",
            "password": password,
            "email_optional": f"{username}@example.local",
        },
    )
    assert response.status_code == 200
    return login_headers(client, username, password)


def create_participant_declaration(client, headers: dict[str, str]) -> str:
    profile = client.get("/api/v1/profiles/me", headers=headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=headers).json()["data"][0]
    response = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile["id"], "plan_id": plan["id"]},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


def create_participant_plan(client, headers: dict[str, str], title: str = "Private Plan") -> dict:
    payload = {
        "title": title,
        "duration_weeks": 12,
        "goal_category": "wellness",
        "summary": "Private plan summary",
        "phases": [{"phase_number": 1, "week_start": 1, "week_end": 4, "objective": "Private phase", "calorie_target": 2000, "macro_targets_json": {"protein": 100}, "habits_json": [], "success_metrics_json": []}],
    }
    response = client.post("/api/v1/plans", json=payload, headers=headers)
    assert response.status_code == 200
    return response.json()["data"]


def create_second_reviewer(client) -> dict[str, str]:
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    response = client.post(
        "/api/v1/admin/users",
        json={"username": "reviewer_two", "full_name": "Reviewer Two", "password": "ReviewerTwo#2026", "role": "reviewer", "email_optional": "reviewer_two@example.local"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    return login_headers(client, "reviewer_two", "ReviewerTwo#2026")


def test_participant_cannot_access_admin_users(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403


def test_participant_cannot_access_audit_logs(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    response = client.get("/api/v1/audit", headers=headers)
    assert response.status_code == 403


def test_reviewer_cannot_access_admin_users(client):
    headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403


def test_participant_cannot_request_reviewer_correction(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    response = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Not allowed", "sections_json": [{"section": "plan"}], "response_due_hours": 24},
        headers=headers,
    )
    assert response.status_code == 403


def test_reviewer_cannot_create_declaration(client):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    profile = client.get("/api/v1/profiles/me", headers=participant_headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=participant_headers).json()["data"][0]
    response = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile["id"], "plan_id": plan["id"]},
        headers=reviewer_headers,
    )
    assert response.status_code == 403


def test_participant_cannot_void_declaration(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    response = client.post(
        f"/api/v1/declarations/{package['id']}/void",
        json={"reason_text": "Not allowed"},
        headers=headers,
    )
    assert response.status_code == 403


def test_unauthenticated_declarations_access_is_rejected(client):
    response = client.get("/api/v1/declarations")
    assert response.status_code == 401


def test_invalid_token_profile_access_is_rejected(client):
    response = client.get("/api/v1/profiles/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401


def test_second_participant_cannot_view_first_participant_declaration(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    package_id = create_participant_declaration(client, owner_headers)
    response = client.get(f"/api/v1/declarations/{package_id}", headers=outsider_headers)
    assert response.status_code == 403


def test_second_participant_cannot_accept_first_participant_package(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    package_id = create_participant_declaration(client, owner_headers)
    upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=admin_headers,
        files={"upload": ("owner-final.txt", BytesIO(b"owner final"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    response = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"delivery_file_id": upload.json()["data"]["id"], "confirmation_note": "Not mine", "accepted_delivery_version": "uploaded"},
        headers=outsider_headers,
    )
    assert response.status_code == 403


def test_second_participant_cannot_mark_first_participant_notification(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    notification = client.get("/api/v1/notifications", headers=owner_headers).json()["data"][0]
    response = client.post(f"/api/v1/notifications/{notification['id']}/read", headers=outsider_headers)
    assert response.status_code == 403


def test_second_participant_has_isolated_declaration_list(client):
    outsider_headers = register_participant(client, "participant_two")
    response = client.get("/api/v1/declarations", headers=outsider_headers)
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_second_participant_has_isolated_notifications(client):
    outsider_headers = register_participant(client, "participant_two")
    response = client.get("/api/v1/notifications", headers=outsider_headers)
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_second_participant_cannot_submit_withdraw_or_reopen_first_participant_package(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    package_id = create_participant_declaration(client, owner_headers)

    submit = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=outsider_headers)
    assert submit.status_code == 403

    client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=owner_headers)
    withdraw = client.post(f"/api/v1/declarations/{package_id}/withdraw", json={}, headers=outsider_headers)
    assert withdraw.status_code == 403

    client.post(f"/api/v1/declarations/{package_id}/withdraw", json={}, headers=owner_headers)
    reopen = client.post(f"/api/v1/declarations/{package_id}/reopen", json={}, headers=outsider_headers)
    assert reopen.status_code == 403


def test_second_participant_cannot_acknowledge_or_resubmit_first_participant_correction(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=owner_headers).json()["data"][0]
    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Owner only", "sections_json": [{"section": "plan"}], "response_due_hours": 24},
        headers=reviewer_headers,
    )
    correction_id = correction.json()["data"]["id"]

    acknowledge = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction_id}/acknowledge", json={}, headers=outsider_headers)
    assert acknowledge.status_code == 403

    resubmit = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction_id}/resubmit", json={"reason_text": "No access"}, headers=outsider_headers)
    assert resubmit.status_code == 403


def test_unassigned_reviewer_cannot_access_review_actions(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_reviewer_headers = create_second_reviewer(client)
    package_id = create_participant_declaration(client, owner_headers)
    client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=owner_headers)

    request = client.post(
        f"/api/v1/reviews/{package_id}/request-correction",
        json={"overall_message": "Not assigned", "sections_json": [{"section": "plan"}], "response_due_hours": 24},
        headers=outsider_reviewer_headers,
    )
    assert request.status_code == 403

    corrections = client.get(f"/api/v1/reviews/{package_id}/corrections", headers=outsider_reviewer_headers)
    assert corrections.status_code == 403

    complete = client.post(f"/api/v1/reviews/{package_id}/complete", json={"note": "Not assigned"}, headers=outsider_reviewer_headers)
    assert complete.status_code == 403


def test_second_participant_cannot_access_first_participant_plan_and_versions(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    plan = create_participant_plan(client, owner_headers, title="Owner Plan")
    versions = client.get(f"/api/v1/plans/{plan['id']}/versions", headers=owner_headers)
    version_id = versions.json()["data"][0]["id"]

    get_plan = client.get(f"/api/v1/plans/{plan['id']}", headers=outsider_headers)
    assert get_plan.status_code == 403
    get_versions = client.get(f"/api/v1/plans/{plan['id']}/versions", headers=outsider_headers)
    assert get_versions.status_code == 403
    get_version = client.get(f"/api/v1/plans/versions/{version_id}", headers=outsider_headers)
    assert get_version.status_code == 403


def test_second_participant_cannot_access_first_participant_profile_version(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    versions = client.get("/api/v1/profiles/me/history", headers=owner_headers).json()["data"]
    version_id = versions[0]["id"]
    response = client.get(f"/api/v1/profiles/me/history/{version_id}", headers=outsider_headers)
    assert response.status_code == 403


def test_second_participant_cannot_view_first_participant_acceptance_history(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_two")
    package_id = create_participant_declaration(client, owner_headers)
    response = client.get(f"/api/v1/deliveries/{package_id}/acceptance", headers=outsider_headers)
    assert response.status_code == 403


def test_disabled_user_token_is_rejected_on_subsequent_requests(client):
    user_headers = login_headers(client, "participant_demo", "Participant#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(item for item in users if item["username"] == "participant_demo")
    disable = client.patch(f"/api/v1/admin/users/{participant['id']}", json={"status": "disabled", "is_active": False}, headers=admin_headers)
    assert disable.status_code == 200
    response = client.get("/api/v1/declarations", headers=user_headers)
    assert response.status_code == 403


def test_download_link_cross_binding_is_rejected(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    package_a = create_participant_declaration(client, headers)
    package_b = create_participant_declaration(client, headers)

    upload = client.post(
        f"/api/v1/deliveries/{package_a}/files",
        headers=admin_headers,
        files={"upload": ("cross-bind.txt", BytesIO(b"cross bind"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]

    response = client.post(f"/api/v1/deliveries/{package_b}/links", json={"delivery_file_id": file_id}, headers=admin_headers)
    assert response.status_code == 409


def test_participant_cannot_publish_delivery_files_or_links(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package_id = create_participant_declaration(client, participant_headers)
    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=participant_headers)
    assert submitted.status_code == 200

    upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=participant_headers,
        files={"upload": ("participant-file.txt", BytesIO(b"participant content"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 403

    reviewer_upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=reviewer_headers,
        files={"upload": ("reviewer-file.txt", BytesIO(b"reviewer content"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert reviewer_upload.status_code == 200
    file_id = reviewer_upload.json()["data"]["id"]

    link = client.post(f"/api/v1/deliveries/{package_id}/links", json={"delivery_file_id": file_id}, headers=participant_headers)
    assert link.status_code == 403


def test_participant_cannot_access_admin_only_import_export_settings_and_archives(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    assert client.get("/api/v1/imports", headers=participant_headers).status_code == 403
    assert client.get("/api/v1/exports", headers=participant_headers).status_code == 403
    assert client.get("/api/v1/admin/field-mappings", headers=participant_headers).status_code == 403
    assert client.get("/api/v1/admin/masking-policies", headers=participant_headers).status_code == 403
    assert client.get("/api/v1/admin/settings", headers=participant_headers).status_code == 403
    assert client.get("/api/v1/admin/audit-archives", headers=participant_headers).status_code == 403


def test_participant_cannot_complete_review(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]
    response = client.post(f"/api/v1/reviews/{package['id']}/complete", json={"note": "forbidden"}, headers=participant_headers)
    assert response.status_code == 403


def test_reviewer_declaration_list_only_shows_assigned_packages(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    second_reviewer_headers = create_second_reviewer(client)
    package_id = create_participant_declaration(client, owner_headers)
    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=owner_headers)
    assert submitted.status_code == 200

    second_reviewer_list = client.get("/api/v1/declarations", headers=second_reviewer_headers)
    assert second_reviewer_list.status_code == 200
    assert second_reviewer_list.json()["data"] == []

    assigned_reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    assigned_reviewer_list = client.get("/api/v1/declarations", headers=assigned_reviewer_headers)
    assert assigned_reviewer_list.status_code == 200
    assert any(item["id"] == package_id for item in assigned_reviewer_list.json()["data"])


def test_forced_password_change_is_enforced_server_side_until_completed(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(item for item in users if item["username"] == "participant_demo")

    reset = client.post(
        f"/api/v1/admin/users/{participant['id']}/reset-password",
        json={"new_password": "ResetPass#2026"},
        headers=admin_headers,
    )
    assert reset.status_code == 200

    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "ResetPass#2026"})
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    blocked = client.get("/api/v1/declarations", headers=headers)
    assert blocked.status_code == 403
    assert "Password change required" in blocked.text

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200

    changed = client.post(
        "/api/v1/auth/complete-forced-password-change",
        json={"new_password": "ChangedAgain#2026"},
        headers=headers,
    )
    assert changed.status_code == 200

    relogin = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "ChangedAgain#2026"})
    assert relogin.status_code == 200
    new_headers = {"Authorization": f"Bearer {relogin.json()['data']['access_token']}"}
    allowed = client.get("/api/v1/declarations", headers=new_headers)
    assert allowed.status_code == 200


def test_download_token_cannot_be_used_by_other_participant_even_if_token_exists(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    outsider_headers = register_participant(client, "participant_three")
    package_id = create_participant_declaration(client, owner_headers)
    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=owner_headers)
    assert submitted.status_code == 200
    upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=reviewer_headers,
        files={"upload": ("owner-file.txt", BytesIO(b"owner content"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]
    link = client.post(f"/api/v1/deliveries/{package_id}/links", json={"delivery_file_id": file_id}, headers=reviewer_headers)
    assert link.status_code == 200
    token = link.json()["data"]["token"]

    response = client.get(f"/api/v1/downloads/{token}", headers=outsider_headers)
    assert response.status_code == 403


def test_only_participant_owner_can_confirm_delivery_acceptance(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    package_id = create_participant_declaration(client, participant_headers)
    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=participant_headers)
    assert submitted.status_code == 200
    upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=reviewer_headers,
        files={"upload": ("acceptance-final.txt", BytesIO(b"acceptance final"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]

    reviewer_attempt = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"delivery_file_id": file_id, "confirmation_note": "Reviewer cannot accept", "accepted_delivery_version": "uploaded"},
        headers=reviewer_headers,
    )
    assert reviewer_attempt.status_code == 403

    admin_attempt = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"delivery_file_id": file_id, "confirmation_note": "Admin cannot accept", "accepted_delivery_version": "uploaded"},
        headers=admin_headers,
    )
    assert admin_attempt.status_code == 403

    participant_attempt = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"delivery_file_id": file_id, "confirmation_note": "Owner accepts", "accepted_delivery_version": "uploaded"},
        headers=participant_headers,
    )
    assert participant_attempt.status_code == 200
