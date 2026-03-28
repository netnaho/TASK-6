"""Cross-user data isolation and unassigned reviewer visibility coverage."""

from io import BytesIO

from API_tests.conftest import login_headers


def register_participant(client, username: str, password: str = "ParticipantIso#2026"):
    response = client.post("/api/v1/auth/register", json={"username": username, "full_name": username, "password": password, "email_optional": f"{username}@example.local"})
    assert response.status_code == 200
    return login_headers(client, username, password)


def create_plan_for_user(client, headers, title="Isolated Plan"):
    client.put("/api/v1/profiles/me", json={"profile_status": "complete", "demographics_json": {"age": 30}, "medical_flags_json": {}, "activity_json": {}, "anthropometrics_json": {}, "sensitive": {}}, headers=headers)
    response = client.post(
        "/api/v1/plans",
        json={"title": title, "duration_weeks": 12, "goal_category": "wellness", "summary": "iso", "phases": [{"phase_number": 1, "week_start": 1, "week_end": 4, "objective": "iso", "calorie_target": 2000, "macro_targets_json": {}, "habits_json": [], "success_metrics_json": []}]},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_participant_cannot_see_other_participant_plans_profiles_deliveries_or_corrections(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    outsider_headers = register_participant(client, "participant_iso_two")

    owner_plan = create_plan_for_user(client, owner_headers, title="Owner Private Plan")
    owner_versions = client.get(f"/api/v1/plans/{owner_plan['id']}/versions", headers=owner_headers).json()["data"]
    owner_profile_versions = client.get("/api/v1/profiles/me/history", headers=owner_headers).json()["data"]

    package = client.get("/api/v1/declarations", headers=owner_headers).json()["data"][0]
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Private correction", "sections_json": [{"section": "phase_1"}], "response_due_hours": 24},
        headers=reviewer_headers,
    )
    assert correction.status_code == 200
    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("private.txt", BytesIO(b"private"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 200

    outsider_plans = client.get("/api/v1/plans", headers=outsider_headers)
    assert all(item["id"] != owner_plan["id"] for item in outsider_plans.json()["data"])
    assert client.get(f"/api/v1/plans/{owner_plan['id']}", headers=outsider_headers).status_code == 403
    assert client.get(f"/api/v1/plans/versions/{owner_versions[0]['id']}", headers=outsider_headers).status_code == 403
    assert client.get(f"/api/v1/profiles/me/history/{owner_profile_versions[0]['id']}", headers=outsider_headers).status_code == 403
    assert client.get(f"/api/v1/deliveries/{package['id']}", headers=outsider_headers).status_code == 403
    assert client.get(f"/api/v1/deliveries/{package['id']}/acceptance", headers=outsider_headers).status_code == 403
    assert client.get(f"/api/v1/declarations/{package['id']}/corrections", headers=outsider_headers).status_code == 403


def test_unassigned_reviewer_cannot_see_unassigned_package_resources(client):
    owner_headers = login_headers(client, "participant_demo", "Participant#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    create = client.post(
        "/api/v1/admin/users",
        json={"username": "reviewer_isolated", "full_name": "Reviewer Isolated", "password": "ReviewerIsolated#2026", "role": "reviewer", "email_optional": "isolated@example.local"},
        headers=admin_headers,
    )
    assert create.status_code == 200
    outsider_reviewer_headers = login_headers(client, "reviewer_isolated", "ReviewerIsolated#2026")
    package = client.get("/api/v1/declarations", headers=owner_headers).json()["data"][0]
    assert client.get(f"/api/v1/reviews/{package['id']}/corrections", headers=outsider_reviewer_headers).status_code == 403
    assert client.get(f"/api/v1/deliveries/{package['id']}/acceptance", headers=outsider_reviewer_headers).status_code == 403
