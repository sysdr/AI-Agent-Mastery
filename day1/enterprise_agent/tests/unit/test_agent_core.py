import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from agent.core import AgentCore

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization process"""
    with patch('google.generativeai.configure'):
        agent = AgentCore()
        
        # Mock database setup
        with patch.object(agent, '_setup_database'), \
             patch.object(agent, '_load_state'), \
             patch.object(agent, '_validate_config'):
            
            result = await agent.initialize()
            assert result is True
            assert agent.is_running is True

@pytest.mark.asyncio
async def test_process_request():
    """Test request processing"""
    with patch('google.generativeai.configure'):
        agent = AgentCore()
        agent.is_running = True
        
        # Mock the AI generation
        with patch.object(agent, '_generate_response', return_value="Test response"), \
             patch.object(agent, '_update_state'):
            
            result = await agent.process_request("Hello")
            
            assert result['status'] == 'success'
            assert result['response'] == "Test response"
            assert 'request_id' in result

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in request processing"""
    with patch('google.generativeai.configure'):
        agent = AgentCore()
        agent.is_running = True
        
        # Mock an error in AI generation
        with patch.object(agent, '_generate_response', side_effect=Exception("API Error")), \
             patch.object(agent, '_update_state'):
            
            result = await agent.process_request("Hello")
            
            assert result['status'] == 'error'
            assert 'error_type' in result

@pytest.mark.asyncio
async def test_cleanup():
    """Test agent cleanup process"""
    with patch('google.generativeai.configure'):
        agent = AgentCore()
        agent.is_running = True
        
        # Mock engine disposal
        mock_engine = Mock()
        mock_engine.dispose = Mock()
        agent.engine = mock_engine
        
        # Mock the _update_state method with an async mock
        from unittest.mock import AsyncMock
        agent._update_state = AsyncMock()
        
        # Mock the logger to avoid any logging issues
        agent.logger = Mock()
        
        await agent.cleanup()
        
        assert agent.is_running is False
        mock_engine.dispose.assert_called_once()
