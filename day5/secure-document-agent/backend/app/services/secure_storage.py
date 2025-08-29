from typing import Dict, Any, List, Optional
import os
import json
import uuid
from datetime import datetime
import aiofiles
import hashlib
from cryptography.fernet import Fernet
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class SecureStorage:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        self.encryption_key = settings.ENCRYPTION_KEY.encode()[:32]  # Ensure 32 bytes
        self.cipher = Fernet(Fernet.generate_key())
        
        # Create storage directories
        os.makedirs(f"{self.storage_path}/documents", exist_ok=True)
        os.makedirs(f"{self.storage_path}/metadata", exist_ok=True)
        os.makedirs(f"{self.storage_path}/access_logs", exist_ok=True)
    
    async def store_document(
        self, 
        content: bytes, 
        metadata: Dict[str, Any], 
        pii_info: Any, 
        user_id: str
    ) -> str:
        """Store document with encryption and access controls"""
        try:
            document_id = str(uuid.uuid4())
            
            # Encrypt document content
            encrypted_content = self.cipher.encrypt(content)
            
            # Store encrypted document
            doc_path = f"{self.storage_path}/documents/{document_id}.enc"
            async with aiofiles.open(doc_path, 'wb') as f:
                await f.write(encrypted_content)
            
            # Prepare document metadata
            doc_metadata = {
                "document_id": document_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "file_metadata": metadata,
                "pii_summary": pii_info.get_summary(),
                "access_level": self._determine_access_level(pii_info),
                "encryption_info": {
                    "algorithm": "Fernet",
                    "key_id": hashlib.sha256(self.encryption_key).hexdigest()[:16]
                },
                "compliance_flags": pii_info.compliance_flags,
                "risk_level": pii_info.risk_level
            }
            
            # Store metadata
            metadata_path = f"{self.storage_path}/metadata/{document_id}.json"
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(doc_metadata, indent=2))
            
            # Log storage event
            await self._log_storage_event(document_id, user_id, "stored")
            
            return document_id
            
        except Exception as e:
            logger.error(f"Document storage error: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Retrieve document with metadata"""
        try:
            # Load metadata
            metadata_path = f"{self.storage_path}/metadata/{document_id}.json"
            if not os.path.exists(metadata_path):
                raise FileNotFoundError("Document not found")
            
            async with aiofiles.open(metadata_path, 'r') as f:
                metadata = json.loads(await f.read())
            
            # Load encrypted document
            doc_path = f"{self.storage_path}/documents/{document_id}.enc"
            async with aiofiles.open(doc_path, 'rb') as f:
                encrypted_content = await f.read()
            
            # Decrypt content
            decrypted_content = self.cipher.decrypt(encrypted_content)
            
            return {
                "document_id": document_id,
                "content": decrypted_content,
                "metadata": metadata,
                "access_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document retrieval error: {str(e)}")
            raise
    
    async def check_access(self, document_id: str, user_id: str) -> bool:
        """Check if user has access to document"""
        try:
            metadata_path = f"{self.storage_path}/metadata/{document_id}.json"
            if not os.path.exists(metadata_path):
                return False
            
            async with aiofiles.open(metadata_path, 'r') as f:
                metadata = json.loads(await f.read())
            
            # Basic access control - owner has access
            # In production, implement RBAC with groups, roles, etc.
            if metadata.get("user_id") == user_id:
                return True
            
            # Check for shared access (would be in a separate table in production)
            shared_users = metadata.get("shared_with", [])
            return user_id in shared_users
            
        except Exception as e:
            logger.error(f"Access check error: {str(e)}")
            return False
    
    async def list_user_documents(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List documents accessible to user"""
        try:
            documents = []
            metadata_dir = f"{self.storage_path}/metadata"
            
            if not os.path.exists(metadata_dir):
                return []
            
            for filename in os.listdir(metadata_dir):
                if not filename.endswith('.json'):
                    continue
                
                metadata_path = os.path.join(metadata_dir, filename)
                async with aiofiles.open(metadata_path, 'r') as f:
                    metadata = json.loads(await f.read())
                
                # Check access
                if await self.check_access(metadata["document_id"], user_id):
                    # Return documents in the format expected by DocumentResponse schema
                    document_data = {
                        "document_id": metadata["document_id"],
                        "filename": metadata["file_metadata"].get("filename", "unknown"),
                        "processing_result": {
                            "text_content": metadata.get("file_metadata", {}).get("content_analysis", {}).get("text_content", ""),
                            "chunks": [],
                            "file_type": metadata["file_metadata"].get("content_type", "unknown"),
                            "content_classification": metadata.get("file_metadata", {}).get("content_analysis", {}).get("category", "unknown"),
                            "chunk_count": 0,
                            "character_count": metadata["file_metadata"].get("file_size", 0)
                        },
                        "pii_summary": metadata.get("pii_summary", {
                            "total_entities": 0,
                            "entity_types": [],
                            "risk_level": metadata.get("risk_level", "low"),
                            "compliance_flags": [],
                            "entities": []
                        }),
                        "metadata": metadata.get("file_metadata", {}),
                        "status": "processed",
                        "uploaded_at": metadata["created_at"]
                    }
                    documents.append(document_data)
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            return documents[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Document listing error: {str(e)}")
            return []
    
    def _determine_access_level(self, pii_info) -> str:
        """Determine access level based on PII content"""
        if pii_info.risk_level == "high":
            return "restricted"
        elif pii_info.risk_level == "medium":
            return "controlled"
        else:
            return "standard"
    
    async def _log_storage_event(self, document_id: str, user_id: str, action: str):
        """Log storage access events"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "document_id": document_id,
                "user_id": user_id,
                "action": action,
                "source": "secure_storage"
            }
            
            log_file = f"{self.storage_path}/access_logs/{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Storage logging error: {str(e)}")
