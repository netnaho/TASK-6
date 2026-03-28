from io import BytesIO

from API_tests.conftest import login_headers
from app.models.delivery import DownloadToken
from app.security.tokens import hash_download_token
from app.utils.datetime import add_hours


def test_delivery_download_valid_vs_expired(client, db_session):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    upload = client.post(
        f"/api/v1/deliveries/{package['id']}/files",
        headers=reviewer_headers,
        files={"upload": ("note.txt", BytesIO(b"hello"), "text/plain")},
        data={"file_type": "revision_note", "is_final": "false"},
    )
    assert upload.status_code == 200
    file_id = upload.json()["data"]["id"]
    link = client.post(f"/api/v1/deliveries/{package['id']}/links", json={"delivery_file_id": file_id}, headers=reviewer_headers)
    token = link.json()["data"]["token"]
    valid = client.get(f"/api/v1/downloads/{token}", headers=headers)
    assert valid.status_code == 200
    token_row = db_session.query(DownloadToken).filter(DownloadToken.token_hash == hash_download_token(token)).one()
    token_row.expires_at = add_hours(-1)
    db_session.add(token_row)
    db_session.commit()
    expired = client.get(f"/api/v1/downloads/{token}", headers=headers)
    assert expired.status_code == 401


def test_bulk_delivery_download(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    reviewer_headers = login_headers(client, "reviewer_demo", "Reviewer#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]

    for name, content in [("note-one.txt", b"hello one"), ("note-two.txt", b"hello two")]:
        upload = client.post(
            f"/api/v1/deliveries/{package['id']}/files",
            headers=reviewer_headers,
            files={"upload": (name, BytesIO(content), "text/plain")},
            data={"file_type": "revision_note", "is_final": "false"},
        )
        assert upload.status_code == 200

    bulk = client.post(f"/api/v1/deliveries/{package['id']}/bulk-download", headers=headers)
    assert bulk.status_code == 200
    token = bulk.json()["data"]["token"]
    download = client.get(f"/api/v1/downloads/{token}", headers=headers)
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/zip"
