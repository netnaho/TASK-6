"""Timestamp population and expiry/deadline behavior coverage."""

from io import BytesIO

from API_tests.conftest import login_headers
from app.models.declaration import CorrectionRequest
from app.models.delivery import DownloadToken
from app.security.tokens import hash_download_token
from app.utils.datetime import add_hours


def test_submission_assignment_and_acceptance_timestamps(client):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]
    assert package["submitted_at"] is not None
    assert package["review_due_at"] is not None

    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("timestamp-final.txt", BytesIO(b"timestamp final"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "true"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]

    acceptance = client.post(
        f"/api/v1/deliveries/{package['id']}/acceptance",
        json={"delivery_file_id": file_id, "confirmation_note": "Accept", "accepted_delivery_version": "uploaded"},
        headers=participant_headers,
    )
    assert acceptance.status_code == 200
    refreshed = client.get(f"/api/v1/declarations/{package['id']}", headers=participant_headers)
    assert refreshed.json()["data"]["accepted_at"] is not None


def test_expired_download_tokens_and_correction_deadlines_are_enforced(client, db_session):
    participant_headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=participant_headers).json()["data"][0]

    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("expiry.txt", BytesIO(b"expiry"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    file_id = upload.json()["data"]["id"]
    link = client.post(f"/api/v1/deliveries/{package['id']}/links", json={"delivery_file_id": file_id}, headers=reviewer_headers)
    token = link.json()["data"]["token"]
    row = db_session.query(DownloadToken).filter(DownloadToken.token_hash == hash_download_token(token)).one()
    row.expires_at = add_hours(-1)
    db_session.add(row)
    db_session.commit()
    expired = client.get(f"/api/v1/downloads/{token}", headers=participant_headers)
    assert expired.status_code == 401

    correction = client.post(
        f"/api/v1/reviews/{package['id']}/request-correction",
        json={"overall_message": "Deadline check", "sections_json": [{"section": "phase_1"}], "response_due_hours": 24},
        headers=reviewer_headers,
    )
    correction_id = correction.json()["data"]["id"]
    correction_row = db_session.query(CorrectionRequest).filter(CorrectionRequest.id == correction_id).one()
    correction_row.response_due_at = add_hours(-1)
    db_session.add(correction_row)
    db_session.commit()

    acknowledge = client.post(f"/api/v1/declarations/{package['id']}/corrections/{correction_id}/acknowledge", json={}, headers=participant_headers)
    assert acknowledge.status_code == 409
