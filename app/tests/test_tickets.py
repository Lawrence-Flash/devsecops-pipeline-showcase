"""Ticket validation, storage, and the rate limit."""

from app.tests.conftest import AUTH


def test_create_and_fetch_ticket(client):
    created = client.post(
        "/tickets",
        headers=AUTH,
        json={"title": "Pipeline gate", "body": "Secrets should never reach main."},
    )
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["id"] == 1
    assert ticket["title"] == "Pipeline gate"
    assert "T" in ticket["created_at"]

    fetched = client.get(f"/tickets/{ticket['id']}", headers=AUTH)
    assert fetched.status_code == 200
    assert fetched.json()["body"] == "Secrets should never reach main."

    listing = client.get("/tickets", headers=AUTH)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_blank_and_oversized_input_is_rejected(client):
    blank = client.post("/tickets", headers=AUTH, json={"title": "   ", "body": "ok"})
    assert blank.status_code == 422

    missing = client.post("/tickets", headers=AUTH, json={"title": "only title"})
    assert missing.status_code == 422

    huge = client.post(
        "/tickets",
        headers=AUTH,
        json={"title": "ok", "body": "x" * 4001},
    )
    assert huge.status_code == 422


def test_sql_metacharacters_are_stored_as_data(client):
    payload = {"title": "Robert'); DROP TABLE tickets;--", "body": "still just text"}
    created = client.post("/tickets", headers=AUTH, json=payload)
    assert created.status_code == 201
    listing = client.get("/tickets", headers=AUTH)
    assert listing.status_code == 200
    assert listing.json()[0]["title"] == payload["title"]


def test_unknown_ticket_is_404(client):
    response = client.get("/tickets/999", headers=AUTH)
    assert response.status_code == 404


def test_non_numeric_id_is_rejected(client):
    response = client.get("/tickets/not-an-id", headers=AUTH)
    assert response.status_code == 422


def test_rate_limit_blocks_the_third_write(tight_client):
    body = {"title": "limited", "body": "again"}
    assert tight_client.post("/tickets", headers=AUTH, json=body).status_code == 201
    assert tight_client.post("/tickets", headers=AUTH, json=body).status_code == 201
    blocked = tight_client.post("/tickets", headers=AUTH, json=body)
    assert blocked.status_code == 429
