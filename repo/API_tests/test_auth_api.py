import re

from app.models.user import User

from API_tests.conftest import login_headers


def test_registration_login_and_lockout(client):
    register = client.post("/api/v1/auth/register", json={"username": "new_participant", "full_name": "New Person", "password": "StrongPass#2026", "email_optional": "new@example.local"})
    assert register.status_code == 200
    login = client.post("/api/v1/auth/login", json={"username": "new_participant", "password": "StrongPass#2026"})
    assert login.status_code == 200
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "wrong"})
    locked = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"})
    assert locked.status_code == 401


def test_refresh_flow(client):
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"}).json()["data"]
    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert refresh.status_code == 200


def test_duplicate_registration_conflict(client):
    first = client.post("/api/v1/auth/register", json={"username": "unique_user", "full_name": "Unique User", "password": "StrongPass#2026", "email_optional": "unique@example.local"})
    assert first.status_code == 200
    second = client.post("/api/v1/auth/register", json={"username": "unique_user", "full_name": "Duplicate User", "password": "StrongPass#2026", "email_optional": "duplicate@example.local"})
    assert second.status_code == 409


def test_invalid_and_malformed_bearer_tokens_rejected(client):
    malformed = client.get("/api/v1/declarations", headers={"Authorization": "Bearer definitely-not-a-jwt"})
    assert malformed.status_code == 401
    invalid = client.get("/api/v1/declarations", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert invalid.status_code == 401


def test_captcha_challenge_and_login_flow(client, db_session):
    user = db_session.query(User).filter(User.username == "participant_demo").one()
    user.captcha_required = True
    db_session.add(user)
    db_session.commit()

    challenge = client.get("/api/v1/auth/captcha/challenge")
    assert challenge.status_code == 200
    data = challenge.json()["data"]
    assert data["prompt"]
    assert data["challenge_token"]

    match = re.search(r"What is\s+(\d+)\s*\+\s*(\d+)\?", data["prompt"])
    assert match is not None
    answer = str(int(match.group(1)) + int(match.group(2)))

    success = client.post(
        "/api/v1/auth/login",
        json={
            "username": "participant_demo",
            "password": "Participant#2026",
            "captcha_challenge_token": data["challenge_token"],
            "captcha_answer": answer,
        },
    )
    assert success.status_code == 200

    failure = client.post(
        "/api/v1/auth/login",
        json={
            "username": "participant_demo",
            "password": "Participant#2026",
            "captcha_challenge_token": data["challenge_token"],
            "captcha_answer": "999",
        },
    )
    assert failure.status_code == 422
    assert "Incorrect CAPTCHA answer" in failure.text


def test_refresh_is_rejected_for_disabled_user(client):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"}).json()["data"]
    users = client.get("/api/v1/admin/users", headers=admin_headers).json()["data"]
    participant = next(item for item in users if item["username"] == "participant_demo")
    disabled = client.patch(f"/api/v1/admin/users/{participant['id']}", json={"status": "disabled", "is_active": False}, headers=admin_headers)
    assert disabled.status_code == 200
    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert refresh.status_code == 401


def test_old_refresh_token_is_rejected_after_password_change(client):
    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"})
    assert login.status_code == 200
    tokens = login.json()["data"]

    changed = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "Participant#2026", "new_password": "Participant#2027"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert changed.status_code == 200

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 401

    relogin = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2027"})
    assert relogin.status_code == 200


def test_runtime_setting_can_disable_captcha_enforcement(client, db_session):
    admin_headers = login_headers(client, "admin_demo", "Admin#2026Secure")
    user = db_session.query(User).filter(User.username == "participant_demo").one()
    user.captcha_required = True
    db_session.add(user)
    db_session.commit()

    update = client.put("/api/v1/admin/settings", json={"enable_local_captcha": False}, headers=admin_headers)
    assert update.status_code == 200

    challenge = client.get("/api/v1/auth/captcha/challenge")
    assert challenge.status_code == 200
    assert challenge.json()["data"]["enabled"] is False

    login = client.post("/api/v1/auth/login", json={"username": "participant_demo", "password": "Participant#2026"})
    assert login.status_code == 200
