import pytest
import asyncio
from unittest.mock import Mock, patch
from security.auth import AgentSecurity, CapabilityChecker
from security.quota import QuotaManager

class TestAgentSecurity:
    def test_generate_keypair(self):
        security = AgentSecurity()
        private_key, public_key = security.generate_keypair()
        
        assert private_key is not None
        assert public_key is not None
        assert "BEGIN PRIVATE KEY" in private_key
        assert "BEGIN PUBLIC KEY" in public_key
    
    def test_create_capability_token(self):
        security = AgentSecurity()
        capabilities = {"content.create": True, "content.edit": False}
        
        token = security.create_capability_token(1, capabilities)
        assert token is not None
        
        # Verify token
        payload = security.verify_capability_token(token)
        assert payload is not None
        assert payload["agent_id"] == 1
        assert payload["capabilities"] == capabilities
    
    def test_message_encryption(self):
        security = AgentSecurity()
        message = "Test secret message"
        
        encrypted, session_key = security.encrypt_message(message)
        decrypted = security.decrypt_message(encrypted, session_key)
        
        assert decrypted == message

class TestCapabilityChecker:
    def test_writer_capabilities(self):
        assert CapabilityChecker.has_capability("writer", "content.create") == True
        assert CapabilityChecker.has_capability("writer", "workflow.approve") == False
    
    def test_editor_capabilities(self):
        assert CapabilityChecker.has_capability("editor", "content.create") == True
        assert CapabilityChecker.has_capability("editor", "workflow.approve") == True
    
    def test_invalid_agent_type(self):
        assert CapabilityChecker.has_capability("invalid", "content.create") == False

@pytest.mark.asyncio
class TestQuotaManager:
    async def test_quota_check(self):
        quota_manager = QuotaManager()
        
        # Mock database
        with patch('security.quota.SessionLocal') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.all.return_value = []
            
            result = await quota_manager.check_quota(1, "api_calls", 1)
            assert result == True
