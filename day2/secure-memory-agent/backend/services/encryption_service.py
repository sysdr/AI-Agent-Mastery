from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import os
from app.core.config import settings

class EncryptionService:
    def __init__(self):
        self.master_key = settings.ENCRYPTION_KEY.encode()
    
    def _derive_key(self, conversation_id: str) -> bytes:
        """Derive unique encryption key for conversation"""
        salt = conversation_id.encode()[:16].ljust(16, b'0')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return key
    
    def encrypt_content(self, content: str, conversation_id: str) -> str:
        """Encrypt message content with conversation-specific key"""
        key = self._derive_key(conversation_id)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(content.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_content(self, encrypted_content: str, conversation_id: str) -> str:
        """Decrypt message content"""
        try:
            key = self._derive_key(conversation_id)
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_content.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
