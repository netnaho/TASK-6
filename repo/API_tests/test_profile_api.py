from datetime import datetime

from API_tests.conftest import login_headers


def _assert_iso_8601(value: str):
    assert isinstance(value, str)
    assert value
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_profile_crud(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    payload = {
        "profile_status": "complete",
        "demographics_json": {"age": 33},
        "medical_flags_json": {"diabetes": False},
        "activity_json": {"activity_level": "moderate"},
        "anthropometrics_json": {"height_cm": 170},
        "sensitive": {"clinician_notes": "note"},
    }
    save = client.put("/api/v1/profiles/me", json=payload, headers=headers)
    assert save.status_code == 200
    get_one = client.get("/api/v1/profiles/me", headers=headers)
    assert get_one.status_code == 200
    history = client.get("/api/v1/profiles/me/history", headers=headers)
    assert history.status_code == 200
    rows = history.json()["data"]
    assert rows
    assert rows[0]["version_number"] > rows[-1]["version_number"]
    for row in rows:
        _assert_iso_8601(row["created_at"])

    version = client.get(f"/api/v1/profiles/me/history/{rows[0]['id']}", headers=headers)
    assert version.status_code == 200
    _assert_iso_8601(version.json()["data"]["created_at"])


def test_profile_post_me_upserts_and_returns_envelope(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    payload = {
        "profile_status": "complete",
        "demographics_json": {"age": 28, "gender": "nonbinary"},
        "medical_flags_json": {"has_allergies": True},
        "activity_json": {"activity_level": "high"},
        "anthropometrics_json": {"height_cm": 168, "weight_kg": 60},
        "sensitive": {"allergy_detail": "peanuts", "clinician_notes": "seed-created"},
    }

    created = client.post("/api/v1/profiles/me", json=payload, headers=headers)
    assert created.status_code == 200
    body = created.json()
    assert body["success"] is True
    assert body["message"] == "Profile saved"
    data = body["data"]
    assert data["profile_status"] == "complete"
    assert data["demographics_json"]["age"] == 28
    assert data["anthropometrics_json"]["weight_kg"] == 60
    assert data["sensitive"]["allergy_detail"] == "peanuts"

    fetched = client.get("/api/v1/profiles/me", headers=headers).json()["data"]
    assert fetched["id"] == data["id"]
    assert fetched["current_version_id"] == data["current_version_id"]


def test_profile_post_me_requires_authentication(client):
    response = client.post(
        "/api/v1/profiles/me",
        json={
            "profile_status": "in_progress",
            "demographics_json": {},
            "medical_flags_json": {},
            "activity_json": {},
            "anthropometrics_json": {},
            "sensitive": {},
        },
    )
    assert response.status_code == 401


def test_profile_post_me_rejects_non_participant_roles(client):
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    payload = {
        "profile_status": "in_progress",
        "demographics_json": {},
        "medical_flags_json": {},
        "activity_json": {},
        "anthropometrics_json": {},
        "sensitive": {},
    }

    reviewer_response = client.post("/api/v1/profiles/me", json=payload, headers=reviewer_headers)
    assert reviewer_response.status_code == 403

    admin_response = client.post("/api/v1/profiles/me", json=payload, headers=admin_headers)
    assert admin_response.status_code == 403


def test_profile_post_me_validates_payload_shape(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    response = client.post(
        "/api/v1/profiles/me",
        json={"profile_status": "not-a-valid-status"},
        headers=headers,
    )
    assert response.status_code == 422
