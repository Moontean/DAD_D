from fastapi.testclient import TestClient
from auth_service.main import app

client = TestClient(app)

def test_register_user():
    r = client.post("/register", json={"username": "testuser", "password": "password123"})
    # API returns 200 with a message on success
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") == "User registered successfully"

def test_login_user():
    client.post("/register", json={"username": "testuser", "password": "password123"})
    r = client.post("/login", json={"username": "testuser", "password": "password123"})
    assert r.status_code == 200
    data = r.json()
    # API returns `token` field instead of `access_token`
    assert "token" in data

def test_login_invalid_user():
    r = client.post("/login", json={"username": "invaliduser", "password": "wrongpassword"})
    assert r.status_code == 401