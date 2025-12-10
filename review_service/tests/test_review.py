from fastapi.testclient import TestClient
from review_service.main import app, reviews

client = TestClient(app)

def test_add_review():
    snapshot = {k: [item.copy() for item in v] for k, v in reviews.items()}
    try:
        r = client.post("/reviews", json={"product_id": 1, "username": "tester", "rating": 5, "comment": "Great product!"})
        assert r.status_code == 200
        data = r.json()
        assert data["product_id"] == 1
        assert data["rating"] == 5
        assert data["username"] in ("tester", "anonymous")
        assert "id" in data and "date" in data
    finally:
        reviews.clear(); reviews.update(snapshot)

def test_get_reviews():
    snapshot = {k: [item.copy() for item in v] for k, v in reviews.items()}
    try:
        client.post("/reviews", json={"product_id": 1, "username": "tester", "rating": 4, "comment": "Nice"})
        r = client.get("/reviews/1")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert {"product_id", "rating", "comment", "username"} <= set(data[0].keys())
    finally:
        reviews.clear(); reviews.update(snapshot)