from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import json
import structlog
from datetime import datetime, timedelta
import os
from typing import Dict, Set, Optional, Any
import uuid
import redis.asyncio as redis
import jwt
from models.tenant import TenantModel, UserModel, ConversationModel
from services.gemini_service import GeminiService
from services.tenant_service import TenantService
from services.sync_service import SyncService
from middleware.auth import AuthMiddleware
from middleware.tenant import TenantMiddleware
from config.settings import Settings

logger = structlog.get_logger()
settings = Settings()

app = FastAPI(title="Enterprise Chat Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

# Services
gemini_service = GeminiService()
tenant_service = TenantService()
sync_service = SyncService(redis_client)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.tenant_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, tenant_id: str, user_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "quota_used": 0
        }
        
        if tenant_id not in self.tenant_connections:
            self.tenant_connections[tenant_id] = set()
        self.tenant_connections[tenant_id].add(connection_id)
        
        # Update Redis connection count for quota tracking
        await redis_client.sadd(f"tenant:{tenant_id}:connections", connection_id)
        
        await self.notify_connection_status(tenant_id, user_id, "connected")
    
    async def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            conn_info = self.active_connections[connection_id]
            tenant_id = conn_info["tenant_id"]
            user_id = conn_info["user_id"]
            
            del self.active_connections[connection_id]
            self.tenant_connections[tenant_id].discard(connection_id)
            
            # Remove from Redis connection count for quota tracking
            await redis_client.srem(f"tenant:{tenant_id}:connections", connection_id)
            
            await self.notify_connection_status(tenant_id, user_id, "disconnected")
    
    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]["websocket"]
            await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_tenant(self, tenant_id: str, message: dict, exclude_connection: str = None):
        if tenant_id in self.tenant_connections:
            for connection_id in self.tenant_connections[tenant_id]:
                if connection_id != exclude_connection:
                    await self.send_message(connection_id, message)
    
    async def notify_connection_status(self, tenant_id: str, user_id: str, status: str):
        await sync_service.publish_event(f"tenant:{tenant_id}:connections", {
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })

manager = ConnectionManager()

# Authentication dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        
        if not user_id or not tenant_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "tenant_id": tenant_id, "token_payload": payload}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# WebSocket endpoint
@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str, token: str):
    try:
        # Authenticate WebSocket connection
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        
        if not user_id or not tenant_id:
            await websocket.close(code=1008)
            return
        
        # Check tenant quota
        quota_info = await tenant_service.get_quota_info(tenant_id)
        if quota_info["current_connections"] >= quota_info["max_connections"]:
            await websocket.close(code=1008)
            return
        
        await manager.connect(websocket, connection_id, tenant_id, user_id)
        logger.info("WebSocket connected", connection_id=connection_id, tenant_id=tenant_id, user_id=user_id)
        
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Validate tenant isolation (only if tenant_id is provided in message)
                if message.get("tenant_id") and message.get("tenant_id") != tenant_id:
                    await websocket.close(code=1008)
                    return
                
                # Process message based on type
                if message["type"] == "chat_message":
                    await handle_chat_message(connection_id, message, tenant_id, user_id)
                elif message["type"] == "context_update":
                    await handle_context_update(connection_id, message, tenant_id, user_id)
                elif message["type"] == "heartbeat":
                    await websocket.send_text(json.dumps({"type": "heartbeat_ack"}))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("WebSocket error", error=str(e), connection_id=connection_id)
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
    
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
        await websocket.close(code=1011)
    
    finally:
        await manager.disconnect(connection_id)

async def handle_chat_message(connection_id: str, message: dict, tenant_id: str, user_id: str):
    """Handle chat message with AI response"""
    try:
        # Check rate limiting
        quota_check = await tenant_service.check_message_quota(tenant_id, user_id)
        if not quota_check["allowed"]:
            await manager.send_message(connection_id, {
                "type": "quota_exceeded",
                "message": "Rate limit exceeded"
            })
            return
        
        # Get conversation context
        conversation_id = message.get("conversation_id")
        context = await sync_service.get_conversation_context(tenant_id, conversation_id)
        
        # Generate AI response
        user_message = message["content"]
        
        # Update conversation context
        context["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
        
        # Get AI response from Gemini
        ai_response = await gemini_service.generate_response(
            messages=context["messages"],
            tenant_config=await tenant_service.get_tenant_config(tenant_id)
        )
        
        # Add AI response to context
        context["messages"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update context with conflict resolution
        await sync_service.update_conversation_context(
            tenant_id, conversation_id, context, user_id
        )
        
        # Send response to user
        response_message = {
            "type": "chat_response",
            "conversation_id": conversation_id,
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_message(connection_id, response_message)
        
        # Broadcast to other connections for the same conversation
        await manager.broadcast_to_tenant(
            tenant_id, 
            {**response_message, "type": "context_sync"}, 
            exclude_connection=connection_id
        )
        
        # Update usage metrics
        await tenant_service.update_usage_metrics(tenant_id, user_id, "message_sent")
        
    except Exception as e:
        logger.error("Chat message error", error=str(e), connection_id=connection_id)
        await manager.send_message(connection_id, {
            "type": "error",
            "message": "Failed to process message"
        })

async def handle_context_update(connection_id: str, message: dict, tenant_id: str, user_id: str):
    """Handle real-time context synchronization"""
    try:
        conversation_id = message["conversation_id"]
        context_update = message["context_update"]
        
        # Apply context update with conflict resolution
        updated_context = await sync_service.apply_context_update(
            tenant_id, conversation_id, context_update, user_id
        )
        
        # Broadcast updated context to all connections
        await manager.broadcast_to_tenant(tenant_id, {
            "type": "context_updated",
            "conversation_id": conversation_id,
            "context": updated_context,
            "updated_by": user_id
        })
        
    except Exception as e:
        logger.error("Context update error", error=str(e), connection_id=connection_id)

# REST API endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """SSO integration endpoint"""
    try:
        # Validate SSO token (simplified for demo)
        user_info = await tenant_service.validate_sso_token(credentials["sso_token"])
        
        # Generate JWT token
        token_payload = {
            "user_id": user_info["user_id"],
            "tenant_id": user_info["tenant_id"],
            "roles": user_info["roles"],
            "exp": datetime.utcnow() + timedelta(hours=8)
        }
        
        token = jwt.encode(token_payload, settings.secret_key, algorithm="HS256")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": user_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.get("/tenant/info")
async def get_tenant_info(current_user: dict = Depends(get_current_user)):
    """Get tenant configuration and quota information"""
    tenant_id = current_user["tenant_id"]
    
    tenant_info = await tenant_service.get_tenant_info(tenant_id)
    quota_info = await tenant_service.get_quota_info(tenant_id)
    
    return {
        "tenant_info": tenant_info,
        "quota_info": quota_info
    }

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: dict = Depends(get_current_user)):
    """Get conversation history"""
    tenant_id = current_user["tenant_id"]
    
    context = await sync_service.get_conversation_context(tenant_id, conversation_id)
    return context

@app.post("/conversations")
async def create_conversation(current_user: dict = Depends(get_current_user)):
    """Create new conversation"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user["user_id"]
    
    conversation_id = str(uuid.uuid4())
    initial_context = {
        "conversation_id": conversation_id,
        "tenant_id": tenant_id,
        "created_by": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "messages": [],
        "metadata": {}
    }
    
    await sync_service.create_conversation_context(tenant_id, conversation_id, initial_context)
    
    return {"conversation_id": conversation_id}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
