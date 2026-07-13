"""
test_api.py

Basic API tests using FastAPI's TestClient + a throwaway SQLite DB.
Run with: pytest tests/
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_tripscope.db"

import pytest
from fastapi.testclient import TestClient

from api.main import app
from database.database import Base, engine, SessionLocal
from database.models import Destination


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(
        Destination(
            name="Paris",
            description="City of light.",
            short_description="City of light.",
            popularity_score=90.0,
        )
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_destinations():
    response = client.get("/destinations")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["results"][0]["name"] == "Paris"


def test_search_destinations_no_match():
    response = client.get("/destinations", params={"q": "Nowhere"})
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_destination_not_found():
    response = client.get("/destinations/999")
    assert response.status_code == 404


def test_register_and_login():
    register_resp = client.post(
        "/auth/register", json={"email": "user@example.com", "password": "password123"}
    )
    assert register_resp.status_code == 201

    login_resp = client.post(
        "/auth/login", json={"email": "user@example.com", "password": "password123"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_favorites_require_auth():
    response = client.get("/favorites")
    assert response.status_code == 401
