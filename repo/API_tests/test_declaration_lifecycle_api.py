from datetime import datetime

from API_tests.conftest import login_headers


def _assert_iso_8601(value: str):
    assert isinstance(value, str)
    assert value
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_declaration_lifecycle_endpoints(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    profile = client.get("/api/v1/profiles/me", headers=headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=headers).json()["data"][0]
    created = client.post("/api/v1/declarations", json={"profile_id": profile["id"], "plan_id": plan["id"]}, headers=headers)
    package_id = created.json()["data"]["id"]
    submitted = client.post(f"/api/v1/declarations/{package_id}/submit", json={}, headers=headers)
    assert submitted.status_code == 200
    withdrawn = client.post(f"/api/v1/declarations/{package_id}/withdraw", json={}, headers=headers)
    assert withdrawn.status_code == 200
    reopened = client.post(f"/api/v1/declarations/{package_id}/reopen", json={}, headers=headers)
    assert reopened.status_code == 200
    history = client.get(f"/api/v1/declarations/{package_id}/history", headers=headers)
    assert history.status_code == 200
    versions = history.json()["data"]["versions"]
    assert versions
    for row in versions:
        _assert_iso_8601(row["created_at"])


def test_admin_can_void_declaration_with_reason(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    profile = client.get("/api/v1/profiles/me", headers=participant_headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=participant_headers).json()["data"][0]
    created = client.post(
        "/api/v1/declarations",
        json={"profile_id": profile["id"], "plan_id": plan["id"]},
        headers=participant_headers,
    )
    package_id = created.json()["data"]["id"]

    voided = client.post(
        f"/api/v1/declarations/{package_id}/void",
        json={"reason_text": "Administrative duplicate package cleanup"},
        headers=admin_headers,
    )
    assert voided.status_code == 200
    assert voided.json()["data"]["state"] == "voided"
    assert voided.json()["data"]["voided_at"] is not None
