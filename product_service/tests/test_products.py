import copy
from fastapi.testclient import TestClient
from product_service.main import app, products_db

client = TestClient(app)

def test_list_products():
    r = client.get("/products")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert {"id", "name", "price", "description"} <= set(data[0].keys())

def test_get_product_ok():
    r = client.get("/products/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert "name" in data

def test_get_product_404():
    r = client.get("/products/99999")
    assert r.status_code == 404

def test_create_update_delete_product():
    snapshot = copy.deepcopy(products_db)
    try:
        r = client.post("/products", json={"name": "Test Item", "price": 10.0})
        assert r.status_code == 201
        created = r.json()
        pid = created["id"]

        r = client.put(f"/products/{pid}", json={"name": "Updated", "price": 12.5})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated"

        r = client.delete(f"/products/{pid}")
        assert r.status_code == 200
        assert r.json()["message"] == "Product deleted"
    finally:
        products_db[:] = snapshot