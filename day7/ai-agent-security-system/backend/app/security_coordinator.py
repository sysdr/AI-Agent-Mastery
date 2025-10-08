import asyncio
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Dict, List, Any, Optional
import aioredis
import hashlib

class SecurityCoordinator:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.redis_client = None
        self.security_policies = {
            "max_failed_auths": 5,
            "session_timeout": 3600,
            "encryption_required": True,
            "audit_all_actions": True
        }
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for secure state management"""
        password = os.environ.get('SECURITY_MASTER_KEY', 'default-key-change-in-prod').encode()
        salt = b'security_coordinator_salt'  # In prod, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def initialize(self):
        """Initialize security coordinator"""
        try:
            self.redis_client = await aioredis.from_url("redis://localhost:6379")
            print("✅ Security Coordinator initialized with Redis")
        except Exception as e:
            print(f"⚠️ Redis not available, using in-memory storage: {e}")
    
    async def register_agent(self, agent_id: str, capabilities: List[str], security_level: str) -> str:
        """Register agent with encrypted security context"""
        registration_data = {
            "agent_id": agent_id,
            "capabilities": capabilities,
            "security_level": security_level,
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active",
            "auth_failures": 0
        }
        
        # Encrypt sensitive data
        encrypted_data = self.cipher_suite.encrypt(
            json.dumps(registration_data).encode()
        )
        
        self.agents[agent_id] = {
            "encrypted_data": encrypted_data,
            "last_seen": datetime.utcnow(),
            "security_hash": hashlib.sha256(agent_id.encode()).hexdigest()[:16]
        }
        
        # Store in Redis if available
        if self.redis_client:
            await self.redis_client.setex(
                f"agent:{agent_id}",
                3600,  # 1 hour TTL
                encrypted_data
            )
        
        return agent_id
    
    async def get_agent_context(self, agent_id: str) -> Optional[Dict]:
        """Retrieve and decrypt agent security context"""
        if agent_id not in self.agents:
            return None
        
        try:
            encrypted_data = self.agents[agent_id]["encrypted_data"]
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Failed to decrypt agent context: {e}")
            return None
    
    async def update_agent_status(self, agent_id: str, status_update: Dict):
        """Update agent status with security validation"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        
        current_context = await self.get_agent_context(agent_id)
        if not current_context:
            raise ValueError(f"Cannot retrieve context for agent {agent_id}")
        
        # Update context
        current_context.update(status_update)
        current_context["last_updated"] = datetime.utcnow().isoformat()
        
        # Re-encrypt updated data
        encrypted_data = self.cipher_suite.encrypt(
            json.dumps(current_context).encode()
        )
        
        self.agents[agent_id]["encrypted_data"] = encrypted_data
        self.agents[agent_id]["last_seen"] = datetime.utcnow()
    
    async def get_status(self) -> Dict:
        """Get current security coordinator status"""
        active_agents = 0
        threat_indicators = 0
        
        for agent_id, agent_data in self.agents.items():
            context = await self.get_agent_context(agent_id)
            if context and context.get("status") == "active":
                active_agents += 1
            
            # Check for threat indicators
            if context and context.get("auth_failures", 0) > 3:
                threat_indicators += 1
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "threat_indicators": threat_indicators,
            "threat_level": "high" if threat_indicators > 2 else "low",
            "last_scan": datetime.utcnow().isoformat(),
            "encryption_active": True
        }
    
    async def validate_agent_access(self, agent_id: str, requested_action: str) -> bool:
        """Validate if agent can perform requested action"""
        context = await self.get_agent_context(agent_id)
        if not context:
            return False
        
        # Check security level permissions
        security_level = context.get("security_level", "low")
        capabilities = context.get("capabilities", [])
        
        # Simple access control logic
        if security_level == "high" or requested_action in capabilities:
            return True
        
        return False
