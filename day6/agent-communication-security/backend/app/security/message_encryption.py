from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class MessageEncryption:
    def __init__(self):
        self.master_key = os.getenv("MASTER_KEY", "default-master-key-change-in-production")
        
    def _get_agent_key(self, agent_id: str) -> bytes:
        """Generate agent-specific encryption key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=agent_id.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key
    
    def encrypt_message(self, content: str, agent_id: str) -> str:
        """Encrypt message for specific agent"""
        key = self._get_agent_key(agent_id)
        fernet = Fernet(key)
        encrypted_content = fernet.encrypt(content.encode())
        return base64.urlsafe_b64encode(encrypted_content).decode()
    
    def decrypt_message(self, encrypted_content: str, agent_id: str) -> str:
        """Decrypt message for specific agent"""
        key = self._get_agent_key(agent_id)
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_content.encode())
        decrypted_content = fernet.decrypt(encrypted_bytes)
        return decrypted_content.decode()
