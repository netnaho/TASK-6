from API_tests.conftest import login_headers


def test_reviewer_correction_flow(client):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]
    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Correct phase objective", "sections_json": [{"section": "phase_1", "issue": "clarify target"}], "response_due_hours": 24},
        headers=reviewer_headers,
    )
    assert correction.status_code == 200
    correction_id = correction.json()["data"]["id"]
    acknowledged = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction_id}/acknowledge", json={}, headers=participant_headers)
    assert acknowledged.status_code == 200
    resubmitted = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction_id}/resubmit", json={"reason_text": "Addressed"}, headers=participant_headers)
    assert resubmitted.status_code == 200


def test_reviewer_complete_review_happy_path_and_error_cases(client):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    completed = client.post(f"/api/v1/reviews/{package['id']}/complete", json={"note": "Finalized review"}, headers=reviewer_headers)
    assert completed.status_code == 200
    assert completed.json()["data"]["status"] == "completed"

    queue = client.get("/api/v1/reviews/queue", headers=reviewer_headers)
    assert queue.status_code == 200
    assert all(item["package_id"] != package["id"] for item in queue.json()["data"])

    already_completed = client.post(f"/api/v1/reviews/{package['id']}/complete", json={"note": "Duplicate complete"}, headers=reviewer_headers)
    assert already_completed.status_code == 409

    client.post(
        "/api/v1/admin/users",
        json={"username": "reviewer_unassigned", "full_name": "Reviewer Unassigned", "password": "ReviewerUnassigned#2026", "role": "reviewer", "email_optional": "unassigned@example.local"},
        headers=admin_headers,
    )
    unassigned_headers = login_headers(client, "reviewer_unassigned", "ReviewerUnassigned#2026")
    unassigned = client.post(f"/api/v1/reviews/{package['id']}/complete", json={"note": "Not assigned"}, headers=unassigned_headers)
    assert unassigned.status_code == 403


def test_reviewer_context_exposes_submitted_profile_and_plan(client):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    response = client.get(f"/api/v1/reviews/{package['id']}/context", headers=reviewer_headers)
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["profile_version"]["snapshot_json"]["sensitive"]["allergy_detail"] == "Tree nuts"
    assert payload["plan_version"]["snapshot_json"]["phases"][0]["objective"]
