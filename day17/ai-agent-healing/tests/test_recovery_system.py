import pytest
import asyncio
from backend.app.recovery.auto_recovery import AutoRecoverySystem

@pytest.mark.asyncio
async def test_recovery_system_initialization():
    recovery = AutoRecoverySystem()
    assert len(recovery.recovery_procedures) > 0
    assert recovery.max_recovery_attempts == 3
    assert recovery.recovery_cooldown == 300

@pytest.mark.asyncio
async def test_execute_recovery():
    recovery = AutoRecoverySystem()
    
    # Test CPU recovery
    result = await recovery.execute_recovery("high_cpu")
    
    assert result["trigger"] == "high_cpu"
    assert result["status"] in ["completed", "failed", "in_progress"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_high_cpu_recovery():
    recovery = AutoRecoverySystem()
    recovery_record = {"timestamp": "2024-01-01T00:00:00"}
    
    result = await recovery._recover_high_cpu(recovery_record)
    
    assert result["success"] is True
    assert len(result["steps"]) >= 4
    assert "identified_cpu_processes" in result["steps"]
    assert "validated_security" in result["steps"]
    assert result["duration"] > 0

@pytest.mark.asyncio
async def test_security_breach_recovery():
    recovery = AutoRecoverySystem()
    recovery_record = {"timestamp": "2024-01-01T00:00:00"}
    
    result = await recovery._recover_security_breach(recovery_record)
    
    assert result["success"] is True
    assert "isolated_affected_services" in result["steps"]
    assert "rotated_security_credentials" in result["steps"]
    assert "validated_security_posture" in result["steps"]

if __name__ == "__main__":
    pytest.main([__file__])
