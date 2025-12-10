from fastapi.testclient import TestClient
from main import app, reviews_db

client = TestClient(app)

def test_add_review():
    r = client.post("/reviews", json={"product_id": 1, "user_id": 1, "rating": 5, "comment": "Great product!"})
    assert r.status_code == 201
    data = r.json()
    assert data["product_id"] == 1
    assert data["rating"] == 5

def test_get_reviews():
    client.post("/reviews", json={"product_id": 1, "user_id": 1, "rating": 5, "comment": "Great product!"})
    r = client.get("/reviews/1")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert {"product_id", "user_id", "rating", "comment"} <= set(data[0].keys())