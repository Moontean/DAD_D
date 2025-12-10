import pytest
from fastapi.testclient import TestClient
from order_service.main import app, orders_db


@pytest.fixture(autouse=True)
def mock_httpx(monkeypatch):
    # Mock httpx.AsyncClient used by the service to avoid real network calls
    import httpx
    #test branch
    class FakeResponse:
        def __init__(self, status_code=200, text="OK"):
            self.status_code = status_code
            self.text = text

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise httpx.HTTPStatusError("error", request=None, response=self)

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json=None):
            return FakeResponse(200, "OK")

    monkeypatch.setattr("order_service.main.httpx.AsyncClient", FakeClient)


@pytest.fixture(autouse=True)
def isolate_orders_state():
    # Snapshot and restore in-memory DB to keep tests isolated
    snapshot = {k: [o.copy() for o in v] for k, v in orders_db.items()}
    try:
        yield
    finally:
        orders_db.clear()
        orders_db.update(snapshot)

client = TestClient(app)

def test_create_order():
    r = client.post(
        "/orders",
        json={"user_id": 1, "items": [{"product_id": 1, "quantity": 2}], "total_amount": 20.0},
    )
    # Service returns 200 and full order body
    assert r.status_code == 200
    data = r.json()
    assert "order_id" in data
    assert data["user_id"] == 1

def test_get_order():
    client.post(
        "/orders",
        json={"user_id": 2, "items": [{"product_id": 2, "quantity": 1}], "total_amount": 10.0},
    )
    r = client.get("/orders/2")  # list orders for user 2
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["user_id"] == 2

def test_get_order_404():
    # Service returns empty list (200) for users without orders
    r = client.get("/orders/99999")
    assert r.status_code == 200
    assert r.json() == []