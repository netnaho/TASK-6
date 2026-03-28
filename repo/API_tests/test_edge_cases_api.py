"""404s, validation failures, pagination edges, and empty-state responses."""

from io import BytesIO

from API_tests.conftest import login_headers


def test_nonexistent_ids_return_404(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    missing = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/v1/declarations/{missing}", headers=participant_headers).status_code == 404
    assert client.get(f"/api/v1/plans/{missing}", headers=participant_headers).status_code == 404
    assert client.post(f"/api/v1/reviews/{missing}/complete", json={"note": "missing"}, headers=reviewer_headers).status_code in {403, 404}
    assert client.post(f"/api/v1/admin/users/{missing}/reset-password", json={"new_password": "ResetPass#2026"}, headers=admin_headers).status_code == 404


def test_schema_validation_and_pagination_edges(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")

    bad_register = client.post("/api/v1/auth/register", json={"username": "x", "full_name": "x", "password": "short"})
    assert bad_register.status_code == 422

    page_zero = client.get("/api/v1/declarations?page=0&page_size=2", headers=participant_headers)
    assert page_zero.status_code == 422
    negative = client.get("/api/v1/notifications?page=-1&page_size=2", headers=participant_headers)
    assert negative.status_code == 422
    clamped = client.get("/api/v1/admin/users?page=1&page_size=999", headers=admin_headers)
    assert clamped.status_code == 200
    assert clamped.json()["meta"]["page_size"] == 200


def test_empty_state_endpoints(client):
    participant_headers = client.post(
        "/api/v1/auth/register",
        json={"username": "empty_state_user", "full_name": "Empty State User", "password": "EmptyState#2026", "email_optional": "empty@example.local"},
    )
    assert participant_headers.status_code == 200
    participant_headers = login_headers(client, "empty_state_user", "EmptyState#2026")
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")

    plans = client.get("/api/v1/plans", headers=participant_headers)
    assert plans.status_code == 200
    assert plans.json()["data"] == []

    declarations = client.get("/api/v1/declarations", headers=participant_headers)
    assert declarations.status_code == 200
    assert declarations.json()["data"] == []

    imports = client.get("/api/v1/imports", headers=admin_headers)
    exports = client.get("/api/v1/exports", headers=admin_headers)
    assert imports.status_code == 200 and imports.json()["data"] == []
    assert exports.status_code == 200 and exports.json()["data"] == []

    empty_audit_page = client.get("/api/v1/audit?page=999&page_size=10", headers=admin_headers)
    assert empty_audit_page.status_code == 200
    assert empty_audit_page.json()["data"] == []


def test_invalid_enum_like_admin_and_import_export_inputs_return_422(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(item for item in users if item["username"] == "participant_demo")

    bad_role_create = client.post(
        "/api/v1/admin/users",
        json={
            "username": "bad_role_user",
            "full_name": "Bad Role",
            "password": "BadRole#2026",
            "role": "superadmin",
        },
        headers=admin_headers,
    )
    assert bad_role_create.status_code == 422
    assert "Input should be" in bad_role_create.text

    bad_status_update = client.patch(
        f"/api/v1/admin/users/{participant['id']}",
        json={"status": "deleted"},
        headers=admin_headers,
    )
    assert bad_status_update.status_code == 422
    assert "Input should be" in bad_status_update.text

    bad_role_update = client.patch(
        f"/api/v1/admin/users/{participant['id']}",
        json={"role": "owner"},
        headers=admin_headers,
    )
    assert bad_role_update.status_code == 422
    assert "Input should be" in bad_role_update.text

    bad_profile_status = client.put(
        "/api/v1/profiles/me",
        json={
            "profile_status": "archived",
            "demographics_json": {},
            "medical_flags_json": {},
            "activity_json": {},
            "anthropometrics_json": {},
            "sensitive": {},
        },
        headers=participant_headers,
    )
    assert bad_profile_status.status_code == 422
    assert "Input should be" in bad_profile_status.text

    bad_mapping_format = client.post(
        "/api/v1/admin/field-mappings",
        json={"name": "Bad format map", "entity_type": "declaration", "format": "pdf", "mapping_json": {"a": "b"}},
        headers=admin_headers,
    )
    assert bad_mapping_format.status_code == 422
    assert "Input should be" in bad_mapping_format.text

    bad_mapping_entity_type = client.post(
        "/api/v1/admin/field-mappings",
        json={"name": "Bad entity map", "entity_type": "meal", "format": "csv", "mapping_json": {"a": "b"}},
        headers=admin_headers,
    )
    assert bad_mapping_entity_type.status_code == 422
    assert "Input should be" in bad_mapping_entity_type.text

    bad_export_format = client.post(
        "/api/v1/exports",
        json={"format": "pdf", "scope_type": "declarations"},
        headers=admin_headers,
    )
    assert bad_export_format.status_code == 422
    assert "Input should be" in bad_export_format.text

    bad_export_scope = client.post(
        "/api/v1/exports",
        json={"format": "csv", "scope_type": "profiles"},
        headers=admin_headers,
    )
    assert bad_export_scope.status_code == 422
    assert "Input should be" in bad_export_scope.text

    bad_import_format = client.post(
        "/api/v1/imports",
        headers=admin_headers,
        files={"upload": ("bad.csv", BytesIO(b"Package Number\nPKG-1\n"), "text/csv")},
        data={"format": "pdf", "scope_type": "declarations"},
    )
    assert bad_import_format.status_code == 422
    assert "Input should be" in bad_import_format.text
