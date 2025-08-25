import pytest
from fastapi.testclient import TestClient
from ..app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_conversation():
    response = client.post("/api/memory/conversations", 
                          params={"user_id": "test-user", "title": "Test Conversation"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] == "test-user"
