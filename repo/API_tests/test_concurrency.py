"""Concurrency, replay, and idempotency risk coverage."""

from io import BytesIO

from API_tests.conftest import login_headers
from app.models.declaration import CorrectionRequest
from app.utils.datetime import add_hours


def test_double_submit_same_declaration_conflicts(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    profile = client.get("/api/v1/profiles/me", headers=headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=headers).json()["data"][0]
    package = client.post("/api/v1/declarations", json={"profile_id": profile["id"], "plan_id": plan["id"]}, headers=headers).json()["data"]
    first = client.post(f"/api/v1/declarations/{package['id']}/submit", json={}, headers=headers)
    second = client.post(f"/api/v1/declarations/{package['id']}/submit", json={}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409


def test_double_accept_delivery_is_not_500(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("double-accept.txt", BytesIO(b"double accept"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]
    first = client.post(f"/api/v1/deliveries/{package['id']}/acceptance", json={"delivery_file_id": file_id, "confirmation_note": "once", "accepted_delivery_version": "uploaded"}, headers=headers)
    second = client.post(f"/api/v1/deliveries/{package['id']}/acceptance", json={"delivery_file_id": file_id, "confirmation_note": "twice", "accepted_delivery_version": "uploaded"}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 409


def test_refresh_token_replay_after_rotation_is_rejected(client):
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"}).json()["data"]
    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert rotated.status_code == 200
    assert replay.status_code == 401


def test_repeated_correction_acknowledgment_does_not_duplicate_records(client, db_session):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]
    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Ack once", "sections_json": [{"section": "phase_1"}], "response_due_hours": 24},
        headers=reviewer_headers,
    ).json()["data"]
    first = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction['id']}/acknowledge", json={}, headers=participant_headers)
    second = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction['id']}/acknowledge", json={}, headers=participant_headers)
    assert first.status_code == 200
    assert second.status_code == 200
    count = db_session.query(CorrectionRequest).filter(CorrectionRequest.id == correction["id"]).count()
    assert count == 1
