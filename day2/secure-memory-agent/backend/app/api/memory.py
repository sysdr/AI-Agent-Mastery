from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.db.database import get_db
from services.memory_service import MemoryService
from services.encryption_service import EncryptionService
from services.pii_service import PIIService
from services.context_service import ContextService

router = APIRouter()
logger = structlog.get_logger()

class MessageCreate(BaseModel):
    content: str
    role: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    token_count: int
    created_at: datetime
    pii_detected: bool
    pii_classification: dict

@router.post("/conversations", response_model=dict)
async def create_conversation(
    user_id: str,
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create new secure conversation thread"""
    memory_service = MemoryService(db)
    conversation = await memory_service.create_conversation(user_id, title)
    
    logger.info("Conversation created", 
                conversation_id=conversation.id, 
                user_id=user_id)
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at
    }

@router.post("/messages", response_model=MessageResponse)
async def add_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """Add message with encryption and PII detection"""
    memory_service = MemoryService(db)
    pii_service = PIIService()
    encryption_service = EncryptionService()
    
    # PII detection
    pii_result = await pii_service.detect_pii(message.content)
    
    # Encrypt content
    encrypted_content = encryption_service.encrypt_content(
        message.content, 
        message.conversation_id
    )
    
    # Store message
    stored_message = await memory_service.add_message(
        conversation_id=message.conversation_id,
        role=message.role,
        content_encrypted=encrypted_content,
        pii_detected=pii_result["has_pii"],
        pii_classification=pii_result["classification"]
    )
    
    # Update context window
    context_service = ContextService(db)
    await context_service.update_context_window(message.conversation_id)
    
    logger.info("Message added", 
                message_id=stored_message.id,
                pii_detected=pii_result["has_pii"])
    
    return MessageResponse(
        id=stored_message.id,
        conversation_id=stored_message.conversation_id,
        role=stored_message.role,
        content=message.content,
        token_count=stored_message.token_count,
        created_at=stored_message.created_at,
        pii_detected=stored_message.pii_detected,
        pii_classification=stored_message.pii_classification
    )

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve decrypted conversation messages"""
    memory_service = MemoryService(db)
    encryption_service = EncryptionService()
    
    messages = await memory_service.get_conversation_messages(
        conversation_id, limit
    )
    
    decrypted_messages = []
    for msg in messages:
        content = encryption_service.decrypt_content(
            msg.content_encrypted, 
            conversation_id
        )
        decrypted_messages.append({
            "id": msg.id,
            "role": msg.role,
            "content": content,
            "token_count": msg.token_count,
            "created_at": msg.created_at,
            "pii_detected": msg.pii_detected
        })
    
    return {"messages": decrypted_messages}

@router.get("/conversations/{conversation_id}/context")
async def get_optimized_context(
    conversation_id: str,
    max_tokens: int = 4000,
    db: Session = Depends(get_db)
):
    """Get optimized context window for AI model"""
    context_service = ContextService(db)
    
    context = await context_service.get_optimized_context(
        conversation_id, max_tokens
    )
    
    return {
        "context": context["messages"],
        "token_count": context["token_count"],
        "compression_ratio": context["compression_ratio"]
    }
