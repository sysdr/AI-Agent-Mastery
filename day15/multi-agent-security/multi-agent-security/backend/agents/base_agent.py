import asyncio
import json
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.database import SessionLocal, Agent, AgentMessage, AuditLog
from security.auth import AgentSecurity, CapabilityChecker
from security.quota import QuotaManager
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class BaseAgent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.security = AgentSecurity()
        self.quota_manager = QuotaManager()
        self._load_agent_data()
        
    def _load_agent_data(self):
        """Load agent data from database"""
        db = SessionLocal()
        try:
            agent = db.query(Agent).filter(Agent.id == self.agent_id).first()
            if not agent:
                raise ValueError(f"Agent {self.agent_id} not found")
                
            self.name = agent.name
            self.agent_type = agent.agent_type
            self.capabilities = agent.capabilities
            self.certificate = agent.certificate
            self.private_key = agent.private_key
            
        finally:
            db.close()
    
    async def send_message(self, receiver_id: int, message: str, message_type: str = "general"):
        """Send encrypted message to another agent"""
        # Check capability
        if not self.has_capability("communication.send"):
            await self._log_audit("send_message", "DENIED", {"receiver_id": receiver_id}, False)
            return False
            
        # Check quota
        if not await self.quota_manager.check_quota(self.agent_id, "api_calls", 1):
            await self._log_audit("send_message", "QUOTA_EXCEEDED", {"receiver_id": receiver_id}, False)
            return False
        
        # Encrypt message
        encrypted_content, session_key = self.security.encrypt_message(message)
        
        # Store in database
        db = SessionLocal()
        try:
            msg = AgentMessage(
                sender_id=self.agent_id,
                receiver_id=receiver_id,
                encrypted_content=encrypted_content,
                message_type=message_type,
                session_key=session_key
            )
            db.add(msg)
            db.commit()
            
            # Consume quota
            await self.quota_manager.consume_quota(self.agent_id, "api_calls", 1)
            
            await self._log_audit("send_message", "SUCCESS", {
                "receiver_id": receiver_id,
                "message_type": message_type
            }, True)
            
            return True
            
        finally:
            db.close()
    
    async def receive_messages(self) -> List[Dict[str, Any]]:
        """Retrieve and decrypt messages for this agent"""
        db = SessionLocal()
        try:
            messages = db.query(AgentMessage).filter(
                AgentMessage.receiver_id == self.agent_id
            ).order_by(AgentMessage.timestamp.desc()).limit(50).all()
            
            decrypted_messages = []
            for msg in messages:
                decrypted_content = self.security.decrypt_message(
                    msg.encrypted_content, 
                    msg.session_key
                )
                if decrypted_content:
                    decrypted_messages.append({
                        "id": msg.id,
                        "sender_id": msg.sender_id,
                        "content": decrypted_content,
                        "message_type": msg.message_type,
                        "timestamp": msg.timestamp.isoformat()
                    })
            
            return decrypted_messages
            
        finally:
            db.close()
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has specific capability"""
        return CapabilityChecker.has_capability(self.agent_type, capability)
    
    async def _log_audit(self, action: str, resource: str, details: Dict[str, Any], success: bool):
        """Log audit trail"""
        db = SessionLocal()
        try:
            audit = AuditLog(
                agent_id=self.agent_id,
                action=action,
                resource=resource,
                details=details,
                success=success
            )
            db.add(audit)
            db.commit()
        finally:
            db.close()
    
    async def call_gemini_api(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Call Gemini API with quota management"""
        # Check quota
        cost_estimate = max_tokens * 0.001  # Rough estimate
        if not await self.quota_manager.check_quota(self.agent_id, "cost", cost_estimate):
            return None
            
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Consume quota
            await self.quota_manager.consume_quota(self.agent_id, "api_calls", 1)
            await self.quota_manager.consume_quota(self.agent_id, "cost", cost_estimate)
            
            return response.text
            
        except Exception as e:
            await self._log_audit("gemini_api_call", "ERROR", {"error": str(e)}, False)
            return None
