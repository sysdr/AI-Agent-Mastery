import asyncio
import json
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

class BaseAgent:
    def __init__(self, agent_id: str, permissions: list = None):
        self.agent_id = agent_id
        self.permissions = permissions or ["read"]
        self.status = "inactive"
        
    async def start(self):
        """Start the agent"""
        self.status = "active"
        logger.info("Agent started", agent_id=self.agent_id)
        
    async def stop(self):
        """Stop the agent"""
        self.status = "inactive"
        logger.info("Agent stopped", agent_id=self.agent_id)
        
    async def send_message(self, receiver_id: str, content: str, message_type: str = "text"):
        """Send message to another agent"""
        # This would integrate with the main message sending system
        logger.info("Message sent", 
                   sender=self.agent_id, 
                   receiver=receiver_id, 
                   type=message_type)
        
    async def process_message(self, message: Dict[str, Any]):
        """Process received message"""
        logger.info("Message processed", 
                   agent_id=self.agent_id, 
                   message_id=message.get("id"))
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "permissions": self.permissions
        }
