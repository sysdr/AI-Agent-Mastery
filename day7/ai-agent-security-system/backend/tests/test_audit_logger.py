import pytest
import asyncio
from app.audit_logger import AuditLogger

@pytest.mark.asyncio
async def test_audit_logging():
    logger = AuditLogger()
    await logger.initialize()
    
    test_event = {
        "type": "test_event",
        "agent_id": "test_agent",
        "action": "test_action",
        "data": {"key": "value"}
    }
    
    await logger.log_event(test_event)
    
    entries = await logger.get_entries(limit=1)
    assert len(entries) >= 1
    
    entry = entries[0]
    assert entry["event_type"] == "test_event"
    assert entry["agent_id"] == "test_agent"
    assert entry["verified"] == True

@pytest.mark.asyncio
async def test_audit_integrity():
    logger = AuditLogger()
    await logger.initialize()
    
    # Log multiple events
    for i in range(3):
        await logger.log_event({
            "type": "test_sequence",
            "agent_id": f"agent_{i}",
            "sequence_number": i
        })
    
    entries = await logger.get_entries(limit=10)
    
    # All entries should be verified
    for entry in entries:
        assert entry["verified"] == True
