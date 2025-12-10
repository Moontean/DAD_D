from fastapi.testclient import TestClient
from cart_service.main import app, carts

client = TestClient(app)

def test_add_to_cart():
    snapshot = {k: v.copy() for k, v in carts.items()}
    try:
        user_id = 1
        r = client.post(f"/cart/{user_id}/add", json={"product_id": 1, "quantity": 2})
        assert r.status_code == 200
        data = r.json()
        assert data["message"] in ("Item added", "Item quantity updated")
        assert isinstance(data["cart"], list)
        assert any(item["product_id"] == 1 for item in data["cart"])
    finally:
        carts.clear(); carts.update(snapshot)

def test_view_cart():
    snapshot = {k: v.copy() for k, v in carts.items()}
    try:
        user_id = 2
        client.post(f"/cart/{user_id}/add", json={"product_id": 1, "quantity": 2})
        r = client.get(f"/cart/{user_id}")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert {"product_id", "quantity"} <= set(data[0].keys())
    finally:
        carts.clear(); carts.update(snapshot)

def test_clear_cart():
    snapshot = {k: v.copy() for k, v in carts.items()}
    try:
        user_id = 3
        client.post(f"/cart/{user_id}/add", json={"product_id": 1, "quantity": 2})
        r = client.delete(f"/cart/{user_id}/clear")
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "Cart cleared"
        r = client.get(f"/cart/{user_id}")
        assert r.status_code == 200
        assert r.json() == []
    finally:
        carts.clear(); carts.update(snapshot)