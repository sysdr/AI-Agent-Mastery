from sqlalchemy.orm import Session
from models.conversation import Conversation, Message, AuditLog
from typing import List, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()

class MemoryService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """Create new conversation with audit logging"""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        # Audit log
        await self._log_audit_event("conversation_created", {
            "conversation_id": conversation.id,
            "user_id": user_id
        })
        
        return conversation
    
    async def add_message(
        self, 
        conversation_id: str,
        role: str,
        content_encrypted: str,
        pii_detected: bool = False,
        pii_classification: dict = None
    ) -> Message:
        """Add encrypted message with PII classification"""
        
        # Calculate token count (simplified)
        token_count = len(content_encrypted.split()) * 1.3  # Rough estimate
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content_encrypted=content_encrypted,
            content_hash=self._calculate_hash(content_encrypted),
            token_count=int(token_count),
            pii_detected=pii_detected,
            pii_classification=pii_classification or {}
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Audit log for PII detection
        if pii_detected:
            await self._log_audit_event("pii_detected", {
                "message_id": message.id,
                "conversation_id": conversation_id,
                "classification": pii_classification
            }, security_level="WARNING")
        
        return message
    
    async def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50
    ) -> List[Message]:
        """Retrieve conversation messages"""
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        # Audit log access
        await self._log_audit_event("messages_accessed", {
            "conversation_id": conversation_id,
            "message_count": len(messages)
        })
        
        return list(reversed(messages))
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate content hash for integrity verification"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _log_audit_event(
        self, 
        event_type: str, 
        event_data: dict, 
        security_level: str = "INFO"
    ):
        """Log security audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            event_data=event_data,
            security_level=security_level
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        logger.info(f"Audit event: {event_type}", 
                   data=event_data, 
                   security_level=security_level)
