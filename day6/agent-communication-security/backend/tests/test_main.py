import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_agent():
    response = client.post("/auth/register", json={
        "agent_id": "test-agent-001",
        "permissions": ["read", "write"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["agent_id"] == "test-agent-001"

def test_send_message():
    # First register an agent
    reg_response = client.post("/auth/register", json={
        "agent_id": "sender-agent",
        "permissions": ["read", "write"]
    })
    token = reg_response.json()["token"]
    
    # Send message
    response = client.post("/message/send", 
        json={
            "receiver_id": "receiver-agent",
            "content": "Test encrypted message",
            "type": "text"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message_id" in data
    assert "threat_score" in data

def test_receive_messages():
    # Register agent first
    reg_response = client.post("/auth/register", json={
        "agent_id": "receiver-agent",
        "permissions": ["read"]
    })
    token = reg_response.json()["token"]
    
    # Receive messages
    response = client.get("/messages/receive",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "messages" in data

def test_security_dashboard():
    # Register agent first
    reg_response = client.post("/auth/register", json={
        "agent_id": "dashboard-agent",
        "permissions": ["read", "admin"]
    })
    token = reg_response.json()["token"]
    
    # Get dashboard data
    response = client.get("/security/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data

def test_invalid_token():
    response = client.get("/messages/receive",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
