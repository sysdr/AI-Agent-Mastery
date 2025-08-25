"""
Security component tests
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from security.permission_manager import PermissionManager
from security.audit_logger import AuditLogger
from tools.tool_registry import ToolRegistry

@pytest.mark.asyncio
async def test_permission_manager():
    """Test permission management"""
    pm = PermissionManager()
    await pm.initialize()
    
    # Test permission check
    result = await pm.check_permission(
        "file_agent", "file", "read", 
        path="/home/user/documents/test.txt"
    )
    assert result == True
    
    # Test denied permission
    result = await pm.check_permission(
        "file_agent", "file", "read", 
        path="/etc/passwd"
    )
    assert result == False

@pytest.mark.asyncio
async def test_audit_logger():
    """Test audit logging"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create audit logger with temp directory
        audit_logger = AuditLogger()
        audit_logger.db_path = os.path.join(tmpdir, "test_audit.db")
        await audit_logger.initialize()
        
        # Log an action
        await audit_logger.log_action(
            agent_id="test_agent",
            action="test_action",
            resource="test_resource"
        )
        
        # Retrieve logs
        logs = await audit_logger.get_recent_logs(limit=10)
        assert len(logs) == 1
        assert logs[0]["agent_id"] == "test_agent"

@pytest.mark.asyncio 
async def test_tool_registry():
    """Test tool registry"""
    pm = PermissionManager()
    await pm.initialize()
    
    audit_logger = AuditLogger()
    audit_logger.db_path = ":memory:"
    await audit_logger.initialize()
    
    registry = ToolRegistry(pm, audit_logger)
    await registry.initialize()
    
    # Test tool execution with permission
    result = await registry.execute_tool(
        "file_agent", "list_directory", 
        {"path": "/tmp/user/documents"}
    )
    assert "items" in result

if __name__ == "__main__":
    pytest.main([__file__])
