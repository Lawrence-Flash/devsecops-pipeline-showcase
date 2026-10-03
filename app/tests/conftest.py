"""Pytest setup. Environment is set before the application module is imported."""

import os

os.environ.setdefault("TICKETS_API_KEY", "lab-demo-key")
os.environ.setdefault("DATABASE_PATH", "/tmp/tickets-pytest.db")
os.environ.setdefault("RATE_LIMIT", "30/minute")

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

AUTH = {"X-API-Key": "lab-demo-key"}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TICKETS_API_KEY", "lab-demo-key")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "tickets.db"))
    monkeypatch.setenv("RATE_LIMIT", "30/minute")
    application = create_app()
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture()
def tight_client(tmp_path, monkeypatch):
    monkeypatch.setenv("TICKETS_API_KEY", "lab-demo-key")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "tickets.db"))
    monkeypatch.setenv("RATE_LIMIT", "2/minute")
    application = create_app()
    with TestClient(application) as test_client:
        yield test_client
