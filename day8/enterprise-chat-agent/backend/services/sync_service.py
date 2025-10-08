from typing import Dict, Any, List, Optional
import structlog
import redis.asyncio as redis
import json
from datetime import datetime
import asyncio
import uuid

logger = structlog.get_logger()

class SyncService:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.pubsub = redis_client.pubsub()
    
    async def create_conversation_context(
        self, 
        tenant_id: str, 
        conversation_id: str, 
        initial_context: Dict[str, Any]
    ):
        """Create new conversation context"""
        context_key = f"tenant:{tenant_id}:conversation:{conversation_id}"
        
        # Add vector timestamp for conflict resolution
        initial_context["vector_clock"] = {"created": 1}
        initial_context["last_updated"] = datetime.utcnow().isoformat()
        
        await self.redis_client.set(
            context_key, 
            json.dumps(initial_context),
            ex=86400 * 7  # 7 days expiry
        )
        
        # Log creation event
        await self._log_context_event(tenant_id, conversation_id, "created", initial_context)
    
    async def get_conversation_context(
        self, 
        tenant_id: str, 
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get conversation context with tenant isolation"""
        context_key = f"tenant:{tenant_id}:conversation:{conversation_id}"
        
        context_data = await self.redis_client.get(context_key)
        if context_data:
            return json.loads(context_data)
        
        # Return empty context if not found
        return {
            "conversation_id": conversation_id,
            "tenant_id": tenant_id,
            "messages": [],
            "metadata": {},
            "vector_clock": {"created": 1},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def update_conversation_context(
        self,
        tenant_id: str,
        conversation_id: str,
        updated_context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Update conversation context with conflict resolution"""
        context_key = f"tenant:{tenant_id}:conversation:{conversation_id}"
        
        # Get current context for conflict detection
        current_context = await self.get_conversation_context(tenant_id, conversation_id)
        
        # Implement vector clock for conflict resolution
        updated_context["vector_clock"] = self._increment_vector_clock(
            current_context.get("vector_clock", {}), 
            user_id
        )
        updated_context["last_updated"] = datetime.utcnow().isoformat()
        updated_context["last_updated_by"] = user_id
        
        # Resolve conflicts if necessary
        resolved_context = self._resolve_context_conflicts(current_context, updated_context)
        
        # Store updated context
        await self.redis_client.set(
            context_key,
            json.dumps(resolved_context),
            ex=86400 * 7  # 7 days expiry
        )
        
        # Publish update event for real-time synchronization
        await self.publish_event(f"tenant:{tenant_id}:context_updates", {
            "conversation_id": conversation_id,
            "updated_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "vector_clock": resolved_context["vector_clock"]
        })
        
        # Log update event
        await self._log_context_event(tenant_id, conversation_id, "updated", resolved_context)
        
        return resolved_context
    
    async def apply_context_update(
        self,
        tenant_id: str,
        conversation_id: str,
        context_update: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Apply incremental context update"""
        current_context = await self.get_conversation_context(tenant_id, conversation_id)
        
        # Apply update based on type
        update_type = context_update.get("type")
        
        if update_type == "message_edit":
            message_id = context_update["message_id"]
            new_content = context_update["content"]
            
            # Find and update message
            for msg in current_context["messages"]:
                if msg.get("id") == message_id:
                    msg["content"] = new_content
                    msg["edited"] = True
                    msg["edited_at"] = datetime.utcnow().isoformat()
                    msg["edited_by"] = user_id
                    break
        
        elif update_type == "metadata_update":
            current_context["metadata"].update(context_update["metadata"])
        
        # Update context
        return await self.update_conversation_context(
            tenant_id, conversation_id, current_context, user_id
        )
    
    async def publish_event(self, channel: str, event_data: Dict[str, Any]):
        """Publish event for real-time synchronization"""
        try:
            await self.redis_client.publish(channel, json.dumps(event_data))
        except Exception as e:
            logger.error("Event publish error", error=str(e), channel=channel)
    
    def _increment_vector_clock(
        self, 
        current_clock: Dict[str, int], 
        user_id: str
    ) -> Dict[str, int]:
        """Increment vector clock for conflict resolution"""
        new_clock = current_clock.copy()
        new_clock[user_id] = new_clock.get(user_id, 0) + 1
        return new_clock
    
    def _resolve_context_conflicts(
        self,
        current_context: Dict[str, Any],
        updated_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts using vector clocks and last-write-wins"""
        current_clock = current_context.get("vector_clock", {})
        updated_clock = updated_context.get("vector_clock", {})
        
        # Compare vector clocks to detect conflicts
        current_total = sum(current_clock.values())
        updated_total = sum(updated_clock.values())
        
        if updated_total > current_total:
            # Updated context is newer, use it
            return updated_context
        elif updated_total == current_total:
            # Concurrent update, merge with last-write-wins for metadata
            merged_context = updated_context.copy()
            
            # Merge messages (append-only, no conflicts)
            current_messages = current_context.get("messages", [])
            updated_messages = updated_context.get("messages", [])
            
            if len(updated_messages) > len(current_messages):
                merged_context["messages"] = updated_messages
            
            return merged_context
        else:
            # Current context is newer, keep it
            return current_context
    
    async def _log_context_event(
        self,
        tenant_id: str,
        conversation_id: str,
        event_type: str,
        context_data: Dict[str, Any]
    ):
        """Log context event for audit trail"""
        event_key = f"tenant:{tenant_id}:audit:{conversation_id}:{uuid.uuid4()}"
        
        event_data = {
            "event_type": event_type,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "context_snapshot": context_data,
            "vector_clock": context_data.get("vector_clock", {})
        }
        
        await self.redis_client.set(
            event_key,
            json.dumps(event_data),
            ex=86400 * 30  # 30 days retention
        )
