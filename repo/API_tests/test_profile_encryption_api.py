from sqlalchemy import text

from API_tests.conftest import login_headers


def test_profile_sensitive_payload_uses_db_side_encryption(client, db_session):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    payload = {
        "profile_status": "complete",
        "demographics_json": {"age": 33},
        "medical_flags_json": {"diabetes": False},
        "activity_json": {"activity_level": "moderate"},
        "anthropometrics_json": {"height_cm": 170},
        "sensitive": {
            "allergy_detail": "Sesame",
            "clinician_notes": "Avoid sesame during elimination phase.",
        },
    }

    saved = client.put("/api/v1/profiles/me", json=payload, headers=headers)
    assert saved.status_code == 200
    saved_profile = saved.json()["data"]
    for key, value in payload["sensitive"].items():
        assert saved_profile["sensitive"][key] == value

    fetched = client.get("/api/v1/profiles/me", headers=headers)
    assert fetched.status_code == 200
    for key, value in payload["sensitive"].items():
        assert fetched.json()["data"]["sensitive"][key] == value

    stored_payload = db_session.execute(
        text("SELECT encrypted_payload FROM participant_profiles WHERE id = :id"),
        {"id": saved_profile["id"]},
    ).scalar_one()
    assert isinstance(stored_payload, str)
    assert stored_payload.startswith("-----BEGIN PGP MESSAGE-----")
    assert payload["sensitive"]["allergy_detail"] not in stored_payload
    assert payload["sensitive"]["clinician_notes"] not in stored_payload
