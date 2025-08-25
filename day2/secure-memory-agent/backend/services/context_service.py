from sqlalchemy.orm import Session
from models.conversation import Message, ContextWindow
from .encryption_service import EncryptionService
from typing import Dict, List
import json
import structlog

logger = structlog.get_logger()

class ContextService:
    def __init__(self, db: Session):
        self.db = db
        self.encryption_service = EncryptionService()
    
    async def update_context_window(self, conversation_id: str):
        """Update context window with optimized content"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(20).all()
        
        if not messages:
            return
        
        # Calculate context optimization
        optimized_context = self._optimize_context(messages, conversation_id)
        
        # Store optimized context window
        context_window = ContextWindow(
            conversation_id=conversation_id,
            window_data_encrypted=self.encryption_service.encrypt_content(
                json.dumps(optimized_context), conversation_id
            ),
            token_count=optimized_context["token_count"],
            compression_ratio=optimized_context["compression_ratio"],
            relevance_score=optimized_context["relevance_score"]
        )
        
        self.db.add(context_window)
        self.db.commit()
        
        logger.info("Context window updated", 
                   conversation_id=conversation_id,
                   token_count=optimized_context["token_count"],
                   compression_ratio=optimized_context["compression_ratio"])
    
    async def get_optimized_context(
        self, 
        conversation_id: str, 
        max_tokens: int = 4000
    ) -> Dict:
        """Get optimized context for AI model"""
        
        # Get latest context window
        context_window = self.db.query(ContextWindow).filter(
            ContextWindow.conversation_id == conversation_id
        ).order_by(ContextWindow.created_at.desc()).first()
        
        if not context_window:
            # Fallback to recent messages
            return await self._get_recent_messages_context(conversation_id, max_tokens)
        
        # Decrypt context window
        context_data = json.loads(
            self.encryption_service.decrypt_content(
                context_window.window_data_encrypted, 
                conversation_id
            )
        )
        
        # Trim to max_tokens if needed
        if context_data["token_count"] > max_tokens:
            context_data = self._trim_context(context_data, max_tokens)
        
        return context_data
    
    def _optimize_context(self, messages: List[Message], conversation_id: str) -> Dict:
        """Optimize context using importance scoring"""
        
        total_tokens = 0
        optimized_messages = []
        
        for message in reversed(messages):  # Process oldest first
            # Decrypt message
            content = self.encryption_service.decrypt_content(
                message.content_encrypted, conversation_id
            )
            
            # Calculate importance score
            importance_score = self._calculate_importance(message, content)
            
            # Include message if important or recent
            if importance_score > 0.3 or len(optimized_messages) < 5:
                optimized_messages.append({
                    "role": message.role,
                    "content": content,
                    "token_count": message.token_count,
                    "importance_score": importance_score,
                    "created_at": message.created_at.isoformat()
                })
                total_tokens += message.token_count
        
        # Calculate compression metrics
        original_token_count = sum(msg.token_count for msg in messages)
        compression_ratio = total_tokens / original_token_count if original_token_count > 0 else 1.0
        
        # Calculate overall relevance
        relevance_score = sum(msg["importance_score"] for msg in optimized_messages) / len(optimized_messages) if optimized_messages else 0
        
        return {
            "messages": optimized_messages,
            "token_count": total_tokens,
            "compression_ratio": compression_ratio,
            "relevance_score": relevance_score
        }
    
    def _calculate_importance(self, message: Message, content: str) -> float:
        """Calculate message importance score"""
        score = 0.5  # Base score
        
        # Recency boost
        from datetime import datetime, timedelta
        age_hours = (datetime.utcnow() - message.created_at).total_seconds() / 3600
        recency_score = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
        score += recency_score * 0.3
        
        # Content analysis
        question_indicators = ["?", "how", "what", "when", "where", "why", "can you"]
        if any(indicator in content.lower() for indicator in question_indicators):
            score += 0.2
        
        # User corrections/feedback
        correction_indicators = ["no", "wrong", "correct", "actually", "mistake"]
        if any(indicator in content.lower() for indicator in correction_indicators):
            score += 0.3
        
        # Task-oriented content
        task_indicators = ["help", "create", "generate", "build", "implement", "fix"]
        if any(indicator in content.lower() for indicator in task_indicators):
            score += 0.2
        
        # Length-based importance
        if len(content) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _trim_context(self, context_data: Dict, max_tokens: int) -> Dict:
        """Trim context to fit token limit"""
        messages = context_data["messages"]
        total_tokens = 0
        trimmed_messages = []
        
        # Keep most recent and highest importance messages
        sorted_messages = sorted(
            messages, 
            key=lambda x: (x["importance_score"], x["created_at"]), 
            reverse=True
        )
        
        for message in sorted_messages:
            if total_tokens + message["token_count"] <= max_tokens:
                trimmed_messages.append(message)
                total_tokens += message["token_count"]
            else:
                break
        
        # Sort back chronologically
        trimmed_messages.sort(key=lambda x: x["created_at"])
        
        return {
            "messages": trimmed_messages,
            "token_count": total_tokens,
            "compression_ratio": context_data["compression_ratio"],
            "relevance_score": context_data["relevance_score"]
        }
    
    async def _get_recent_messages_context(self, conversation_id: str, max_tokens: int) -> Dict:
        """Fallback to recent messages"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).all()
        
        if not messages:
            return {"messages": [], "token_count": 0, "compression_ratio": 1.0, "relevance_score": 0}
        
        return self._optimize_context(messages, conversation_id)
