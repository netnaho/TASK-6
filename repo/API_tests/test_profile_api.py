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
    for row in rows:
        _assert_iso_8601(row["created_at"])

    version = client.get(f"/api/v1/profiles/me/history/{rows[0]['id']}", headers=headers)
    assert version.status_code == 200
    _assert_iso_8601(version.json()["data"]["created_at"])
