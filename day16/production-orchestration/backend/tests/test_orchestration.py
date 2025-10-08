"""Test orchestration system components"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator.workflow_engine import WorkflowEngine
from agents.document_agent import DocumentAgent
from security.compliance_checker import ComplianceChecker

@pytest.mark.asyncio
async def test_workflow_engine():
    """Test workflow engine basic functionality"""
    engine = WorkflowEngine()
    
    # Create a test task
    task = await engine.create_task(
        task_id="test_task_1",
        name="Test Document Processing",
        agent_type="document_agent",
        inputs={"test": "data"}
    )
    
    assert task.task_id == "test_task_1"
    assert task.name == "Test Document Processing"
    assert len(engine.active_tasks) == 1

@pytest.mark.asyncio
async def test_document_agent():
    """Test document agent processing"""
    agent = DocumentAgent()
    
    test_docs = [
        {"id": "doc1", "type": "identity", "content": "test content"}
    ]
    
    security_context = {
        "user_id": "test_user",
        "customer_id": "test_customer", 
        "permissions": ["read", "write"]
    }
    
    result = await agent.process_documents(test_docs, security_context)
    
    assert "processed_documents" in result
    assert len(result["processed_documents"]) == 1
    assert result["processed_documents"][0]["status"] == "success"

@pytest.mark.asyncio  
async def test_compliance_checker():
    """Test compliance validation"""
    checker = ComplianceChecker()
    
    test_data = {
        "email": "test@example.com",
        "consent_granted": True,
        "data_purpose": "account_opening"
    }
    
    result = await checker.validate_workflow(
        "customer_onboarding",
        test_data,
        "standard"
    )
    
    assert "approved" in result
    assert isinstance(result["approved"], bool)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
