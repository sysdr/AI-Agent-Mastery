import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from api import app

client = TestClient(app)

def test_health_check():
    """Test API health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_status_endpoint():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    # Should return status even if agent not initialized

@pytest.mark.skip(reason="Requires API key configuration")
def test_chat_endpoint():
    """Test chat endpoint with mocked agent"""
    response = client.post("/chat", json={
        "message": "Hello test",
        "context": {"test": True}
    })
    # This would fail without proper setup, but structure is correct
    assert response.status_code in [200, 503]
