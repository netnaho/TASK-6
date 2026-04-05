from datetime import datetime

from API_tests.conftest import login_headers


def _assert_iso_8601(value: str):
    assert isinstance(value, str)
    assert value
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_plan_crud_and_versions(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    payload = {
        "title": "Performance Reset",
        "duration_weeks": 12,
        "goal_category": "performance",
        "summary": "Twelve-week reset",
        "phases": [{"phase_number": 1, "week_start": 1, "week_end": 4, "objective": "Reset", "calorie_target": 2100, "macro_targets_json": {"protein": 120}, "habits_json": [], "success_metrics_json": []}],
    }
    created = client.post("/api/v1/plans", json=payload, headers=headers)
    assert created.status_code == 200
    plan_id = created.json()["data"]["id"]
    payload["summary"] = "Updated summary"
    updated = client.put(f"/api/v1/plans/{plan_id}", json=payload, headers=headers)
    assert updated.status_code == 200
    versions = client.get(f"/api/v1/plans/{plan_id}/versions", headers=headers)
    assert versions.status_code == 200
    version_rows = versions.json()["data"]
    assert len(version_rows) >= 2
    assert version_rows[0]["version_number"] > version_rows[-1]["version_number"]
    for row in version_rows:
        _assert_iso_8601(row["created_at"])

    version = client.get(f"/api/v1/plans/versions/{version_rows[0]['id']}", headers=headers)
    assert version.status_code == 200
    _assert_iso_8601(version.json()["data"]["created_at"])
