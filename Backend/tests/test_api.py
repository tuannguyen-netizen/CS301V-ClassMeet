import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "testpassword123"})
    assert response.status_code == 200
    assert "token" in response.json()