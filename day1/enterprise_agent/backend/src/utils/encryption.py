from cryptography.fernet import Fernet
import os
from config.settings import settings

class EncryptionManager:
    def __init__(self):
        self.cipher_suite = Fernet(settings.encryption_key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
