from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
import os
import json

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode()[:32]

class AgentSecurity:
    def __init__(self):
        self.jwt_secret = JWT_SECRET_KEY
        
    def generate_agent_keypair(self):
        """Generate RSA key pair for agent"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
    
    def create_capability_token(self, agent_id: int, capabilities: Dict[str, bool], expires_hours: int = 24):
        """Create JWT token with agent capabilities"""
        expire = datetime.utcnow() + timedelta(hours=expires_hours)
        to_encode = {
            "agent_id": agent_id,
            "capabilities": capabilities,
            "exp": expire,
            "type": "capability_token"
        }
        return jwt.encode(to_encode, self.jwt_secret, algorithm="HS256")
    
    def verify_capability_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode capability token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except JWTError:
            return None
    
    def encrypt_message(self, message: str) -> tuple[str, str]:
        """Encrypt message with AES-256 and return encrypted content + session key"""
        # Generate random session key
        session_key = secrets.token_bytes(32)
        iv = secrets.token_bytes(16)
        
        # Encrypt message
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad message to multiple of 16 bytes
        padded_message = message.encode() + b' ' * (16 - len(message.encode()) % 16)
        encrypted_content = iv + encryptor.update(padded_message) + encryptor.finalize()
        
        return encrypted_content.hex(), session_key.hex()
    
    def decrypt_message(self, encrypted_content: str, session_key: str) -> Optional[str]:
        """Decrypt message using session key"""
        try:
            encrypted_bytes = bytes.fromhex(encrypted_content)
            key_bytes = bytes.fromhex(session_key)
            
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
            
            return decrypted_padded.decode().rstrip()
        except Exception:
            return None

class CapabilityChecker:
    """Check agent capabilities for specific actions"""
    
    CAPABILITY_RULES = {
        "writer": {
            "content.create": True,
            "content.draft": True,
            "content.edit_own": True,
            "content.edit_others": False,
            "workflow.approve": False,
            "system.admin": False
        },
        "editor": {
            "content.create": True,
            "content.draft": True,
            "content.edit_own": True,
            "content.edit_others": True,
            "workflow.approve": True,
            "workflow.reject": True,
            "system.admin": False
        },
        "reviewer": {
            "content.create": False,
            "content.draft": False,
            "content.edit_own": False,
            "content.edit_others": False,
            "workflow.approve": True,
            "workflow.reject": True,
            "workflow.publish": True,
            "system.admin": False
        },
        "coordinator": {
            "content.create": True,
            "content.draft": True,
            "content.edit_own": True,
            "content.edit_others": True,
            "workflow.approve": True,
            "workflow.reject": True,
            "workflow.publish": True,
            "workflow.assign": True,
            "system.admin": True
        }
    }
    
    @classmethod
    def has_capability(cls, agent_type: str, capability: str) -> bool:
        """Check if agent type has specific capability"""
        return cls.CAPABILITY_RULES.get(agent_type, {}).get(capability, False)
    
    @classmethod
    def get_capabilities(cls, agent_type: str) -> Dict[str, bool]:
        """Get all capabilities for agent type"""
        return cls.CAPABILITY_RULES.get(agent_type, {})
