"""End-to-end participant, reviewer, delivery, and audit workflow coverage."""

from io import BytesIO

from API_tests.conftest import login_headers


def test_full_participant_reviewer_delivery_lifecycle(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")

    register = client.post(
        "/api/v1/auth/register",
        json={"username": "e2e_participant", "full_name": "E2E Participant", "password": "E2EParticipant#2026", "email_optional": "e2e@example.local"},
    )
    assert register.status_code == 200
    participant_headers = login_headers(client, "e2e_participant", "E2EParticipant#2026")

    profile_payload = {
        "profile_status": "complete",
        "demographics_json": {"age": 35},
        "medical_flags_json": {"allergies": False},
        "activity_json": {"activity_level": "moderate"},
        "anthropometrics_json": {"height_cm": 175},
        "sensitive": {"clinician_notes": "E2E note"},
    }
    profile = client.put("/api/v1/profiles/me", json=profile_payload, headers=participant_headers)
    assert profile.status_code == 200

    plan_payload = {
        "title": "E2E Plan",
        "duration_weeks": 12,
        "goal_category": "wellness",
        "summary": "E2E summary",
        "phases": [{"phase_number": 1, "week_start": 1, "week_end": 4, "objective": "Start strong", "calorie_target": 2100, "macro_targets_json": {"protein": 120}, "habits_json": ["hydrate"], "success_metrics_json": ["consistency"]}],
    }
    plan = client.post("/api/v1/plans", json=plan_payload, headers=participant_headers)
    assert plan.status_code == 200
    plan_id = plan.json()["data"]["id"]

    declaration = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile.json()["data"]["id"], "plan_id": plan_id},
        headers=participant_headers,
    )
    assert declaration.status_code == 200
    package_id = declaration.json()["data"]["id"]

    history_before = client.get(f"/api/v1/declarations/{package_id}/history", headers=participant_headers).json()["data"]
    assert len(history_before["versions"]) == 1

    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=participant_headers)
    assert submitted.status_code == 200
    assert submitted.json()["data"]["submitted_at"] is not None
    assert submitted.json()["data"]["review_due_at"] is not None

    queue = client.get("/api/v1/reviews/queue", headers=reviewer_headers)
    assert queue.status_code == 200
    assert any(item["package_id"] == package_id for item in queue.json()["data"])

    correction = client.post(
        f"/api/v1/reviews/{package_id}/request-correction",
        json={"overall_message": "Please clarify your metrics", "sections_json": [{"section": "phase_1", "issue": "clarify"}], "response_due_hours": 24},
        headers=reviewer_headers,
    )
    assert correction.status_code == 200
    correction_id = correction.json()["data"]["id"]

    acknowledged = client.post(f"/api/v1/declarations/{package_id}/corrections/{correction_id}/acknowledge", json={}, headers=participant_headers)
    assert acknowledged.status_code == 200

    resubmitted = client.post(
        f"/api/v1/declarations/{package_id}/corrections/{correction_id}/resubmit",
        json={"reason_text": "Updated metrics and objectives"},
        headers=participant_headers,
    )
    assert resubmitted.status_code == 200

    completed = client.post(f"/api/v1/reviews/{package_id}/complete", json={"note": "Approved after correction"}, headers=reviewer_headers)
    assert completed.status_code == 200
    assert completed.json()["data"]["status"] == "completed"

    upload = client.post(
        f"/api/v1/deliveries/{package_id}/files",
        headers=reviewer_headers,
        files={"upload": ("final-plan.txt", BytesIO(b"final plan content"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]

    link = client.post(f"/api/v1/deliveries/{package_id}/links", json={"delivery_file_id": file_id}, headers=reviewer_headers)
    assert link.status_code == 200
    token = link.json()["data"]["token"]

    download = client.get(f"/api/v1/downloads/{token}", headers=participant_headers)
    assert download.status_code == 200

    acceptance = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"confirmation_note": "Accepted end-to-end", "accepted_delivery_version": "v1"},
        headers=participant_headers,
    )
    assert acceptance.status_code == 200

    history_after = client.get(f"/api/v1/declarations/{package_id}/history", headers=participant_headers).json()["data"]
    assert len(history_after["versions"]) > len(history_before["versions"])

    notifications = client.get("/api/v1/notifications", headers=participant_headers)
    assert notifications.status_code == 200
    assert len(notifications.json()["data"]) >= 2

    audit = client.get("/api/v1/audit?page=1&page_size=100", headers=admin_headers)
    assert audit.status_code == 200
    actions = [item["action_type"] for item in audit.json()["data"]]
    assert "declaration_create" in actions
    assert "declaration_transition" in actions
    assert "correction_acknowledged" in actions
    assert "review_completed" in actions
