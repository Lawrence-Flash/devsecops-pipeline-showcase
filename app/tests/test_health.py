"""Liveness, readiness, and the public index."""


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_index_has_no_secrets(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "tickets-api"
    assert "key" not in body


def test_interactive_docs_are_off(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
