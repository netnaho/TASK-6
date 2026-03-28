from io import BytesIO

from API_tests.conftest import login_headers


def test_acceptance_confirmation(client):
    headers = login_headers(client, "participant_demo", "Participant#2026")
    package = client.get("/api/v1/declarations", headers=headers).json()["data"][0]
    accept = client.post(f"/api/v1/deliveries/{package['id']}/acceptance", json={"confirmation_note": "Looks good", "accepted_delivery_version": "v1"}, headers=headers)
    assert accept.status_code == 200
    history = client.get(f"/api/v1/deliveries/{package['id']}/acceptance", headers=headers)
    assert history.status_code == 200
    assert len(history.json()["data"]) >= 1
