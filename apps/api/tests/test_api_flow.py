import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_investipet.db"

DB_PATH = "test_investipet.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

from app.main import app  # noqa: E402


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_full_mvp_flow(client: TestClient):
    reg = client.post(
        "/auth/register",
        json={"email": "demo@example.com", "password": "strongpass123", "pet_name": "Milo"},
    )
    assert reg.status_code == 200
    tokens = reg.json()
    access = tokens["access_token"]

    me = client.get("/me", headers=auth_headers(access))
    assert me.status_code == 200
    assert me.json()["pet"]["name"] == "Milo"

    quotes = client.get("/market/quotes")
    assert quotes.status_code == 200
    assert len(quotes.json()) == 20

    buy = client.post(
        "/trades/buy",
        headers=auth_headers(access),
        json={"symbol": "AAPL", "quantity": 2},
    )
    assert buy.status_code == 200

    portfolio = client.get("/portfolio", headers=auth_headers(access))
    assert portfolio.status_code == 200
    assert portfolio.json()["total_value"] > 0

    lessons = client.get("/lessons", headers=auth_headers(access))
    assert lessons.status_code == 200
    lesson_id = lessons.json()[0]["id"]
    quiz = lessons.json()[0]["quiz"]

    submit = client.post(
        f"/lessons/{lesson_id}/submit",
        headers=auth_headers(access),
        json={"answers": {quiz[0]["id"]: quiz[0]["options"][0], quiz[1]["id"]: quiz[1]["options"][0]}, "idempotency_key": "abc123"},
    )
    assert submit.status_code == 200

    shop = client.get("/shop/items", headers=auth_headers(access))
    item_id = shop.json()[0]["id"]

    purchase = client.post("/shop/purchase", headers=auth_headers(access), json={"item_id": item_id})
    assert purchase.status_code == 200

    equip = client.post("/pet/equip", headers=auth_headers(access), json={"item_id": item_id})
    assert equip.status_code == 200
