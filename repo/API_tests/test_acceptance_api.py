from io import BytesIO

from API_tests.conftest import login_headers


def test_acceptance_confirmation(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("final-plan.txt", BytesIO(b"delivered"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]
    accept = client.post(
        f"/api/v1/deliveries/{package['id']}/acceptance",
        json={"delivery_file_id": file_id, "confirmation_note": "Looks good", "accepted_delivery_version": "uploaded"},
        headers=headers,
    )
    assert accept.status_code == 200
    history = client.get(f"/api/v1/deliveries/{package['id']}/acceptance", headers=headers)
    assert history.status_code == 200
    assert len(history.json()["data"]) >= 1


def test_acceptance_requires_delivery_artifact(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    package_id = client.post(
        "/api/v1/declarations",
        json={
            "profile_id": client.get("/api/v1/profiles/me", headers=participant_headers).json()["data"]["id"],
            "plan_id": client.get("/api/v1/plans", headers=participant_headers).json()["data"][0]["id"],
        },
        headers=participant_headers,
    ).json()["data"]["id"]

    accept = client.post(
        f"/api/v1/deliveries/{package_id}/acceptance",
        json={"delivery_file_id": "00000000-0000-0000-0000-000000000000", "confirmation_note": "No files yet", "accepted_delivery_version": "uploaded"},
        headers=participant_headers,
    )
    assert accept.status_code == 409


def test_acceptance_requires_final_artifact_binding(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("draft-note.txt", BytesIO(b"draft note"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 200

    accept = client.post(
        f"/api/v1/deliveries/{package['id']}/acceptance",
        json={"delivery_file_id": upload.json()["data"]["id"], "confirmation_note": "Not final", "accepted_delivery_version": "uploaded"},
        headers=participant_headers,
    )
    assert accept.status_code == 409


def test_acceptance_rejects_version_mismatch(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("final-plan.txt", BytesIO(b"delivered"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200

    accept = client.post(
        f"/api/v1/deliveries/{package['id']}/acceptance",
        json={"delivery_file_id": upload.json()["data"]["id"], "confirmation_note": "Wrong version", "accepted_delivery_version": "v1"},
        headers=participant_headers,
    )
    assert accept.status_code == 409
