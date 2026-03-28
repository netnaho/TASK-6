from io import BytesIO

from API_tests.conftest import login_headers


def test_import_export_and_mapping_tools(client):
    headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    mapping = client.post("/api/v1/admin/field-mappings", json={"name": "Basic map", "entity_type": "declaration", "format": "csv", "mapping_json": {"package_number": "Package Number"}}, headers=headers)
    assert mapping.status_code == 200
    policy = client.post("/api/v1/admin/masking-policies", json={"name": "Mask IDs", "entity_type": "declaration", "rules_json": {"mask_fields": ["participant_id"]}, "is_default": False}, headers=headers)
    assert policy.status_code == 200
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    profile = client.get("/api/v1/profiles/me", headers=participant_headers).json()["data"]
    plan = client.get("/api/v1/plans", headers=participant_headers).json()["data"][0]

    export = client.post("/api/v1/exports", json={"format": "csv", "scope_type": "declarations", "masking_policy_id": policy.json()["data"]["id"]}, headers=headers)
    assert export.status_code == 200
    imported = client.post(
        "/api/v1/imports",
        headers=headers,
        files={"upload": ("rows.csv", BytesIO(f"Package Number,participant_id,profile_id,plan_id,state\nPKG-1,{profile['user_id']},{profile['id']},{plan['id']},draft\n".encode()), "text/csv")},
        data={"format": "csv", "scope_type": "declarations", "mapping_id": mapping.json()["data"]["id"]},
    )
    assert imported.status_code == 200

    audit = client.get("/api/v1/audit?page=1&page_size=200", headers=headers)
    actions = [item["action_type"] for item in audit.json()["data"]]
    assert "data_export" in actions
    assert "data_import" in actions
