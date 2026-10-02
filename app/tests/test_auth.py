"""Authentication and security headers."""

from app.tests.conftest import AUTH


def test_missing_api_key_is_rejected(client):
    response = client.post("/tickets", json={"title": "Hello", "body": "World"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_wrong_api_key_is_rejected(client):
    response = client.post(
        "/tickets",
        headers={"X-API-Key": "not-the-lab-key"},
        json={"title": "Hello", "body": "World"},
    )
    assert response.status_code == 401
    assert "not-the-lab-key" not in response.text


def test_security_headers_on_public_and_error_responses(client):
    for path in ("/health", "/tickets"):
        response = client.get(path)
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert "server" not in response.headers


def test_list_requires_auth(client):
    assert client.get("/tickets").status_code == 401
    assert client.get("/tickets", headers=AUTH).status_code == 200
