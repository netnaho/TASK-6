def test_health_endpoint_returns_ok_without_auth(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok"}


def test_health_endpoint_accepts_only_get(client):
    post = client.post("/health")
    assert post.status_code == 405
    put = client.put("/health")
    assert put.status_code == 405


def test_health_endpoint_sets_request_id_header(client):
    response = client.get("/health", headers={"X-Request-Id": "health-probe-001"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-Id") == "health-probe-001"
