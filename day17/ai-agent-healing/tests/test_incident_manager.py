import pytest
import asyncio
from backend.app.security.incident_manager import IncidentManager

@pytest.mark.asyncio
async def test_incident_manager_initialization():
    manager = IncidentManager()
    assert manager.incidents == []
    assert manager.security_status["threat_level"] == "low"

@pytest.mark.asyncio
async def test_create_incident():
    manager = IncidentManager()
    
    incident = await manager.create_incident(
        "test_attack", 
        "high",
        {"source_ip": "192.168.1.100"}
    )
    
    assert incident["type"] == "test_attack"
    assert incident["severity"] == "high"
    assert incident["status"] == "active"
    assert "id" in incident
    assert len(manager.incidents) == 1

@pytest.mark.asyncio
async def test_simulate_ddos_attack():
    manager = IncidentManager()
    
    result = await manager.simulate_attack("ddos")
    
    assert result["status"] == "attack_simulated"
    assert result["type"] == "ddos"
    assert result["severity"] == "high"
    assert "incident_id" in result
    
    # Check that incident was created
    assert len(manager.incidents) == 1
    incident = manager.incidents[0]
    assert incident["type"] == "ddos"
    assert len(incident["response_actions"]) > 0

@pytest.mark.asyncio
async def test_get_security_status():
    manager = IncidentManager()
    
    # Create a high severity incident
    await manager.create_incident("test_breach", "high", {})
    
    status = await manager.get_security_status()
    
    assert status["threat_level"] == "high"
    assert status["active_incidents"] == 1

if __name__ == "__main__":
    pytest.main([__file__])
