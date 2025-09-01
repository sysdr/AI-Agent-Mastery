from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import redis.asyncio as redis
import json
import asyncio
import logging
from typing import Dict, List
import os
from .auth.jwt_handler import JWTHandler
from .security.message_encryption import MessageEncryption
from .security.threat_monitor import ThreatMonitor
from .agents.base_agent import BaseAgent
from .models.message import SecureMessage
import structlog

# Configure logging
structlog.configure(
    processors=[structlog.dev.ConsoleRenderer()],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global state
redis_client: redis.Redis = None
active_connections: Dict[str, WebSocket] = {}
jwt_handler = JWTHandler()
message_encryption = MessageEncryption()
threat_monitor = ThreatMonitor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # Startup
    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
    await threat_monitor.initialize()
    logger.info("Application started", component="main")
    yield
    # Shutdown
    await redis_client.close()
    logger.info("Application shutdown", component="main")

app = FastAPI(title="Agent Communication Security", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_current_agent(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt_handler.decode_token(credentials.credentials)
        return payload
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.post("/auth/register")
async def register_agent(agent_data: dict):
    """Register a new agent with the system"""
    try:
        agent_id = agent_data["agent_id"]
        permissions = agent_data.get("permissions", ["read"])
        
        # Generate JWT token
        token = jwt_handler.create_token({
            "agent_id": agent_id,
            "permissions": permissions,
            "type": "agent"
        })
        
        # Store agent info in Redis
        await redis_client.hset(f"agent:{agent_id}", mapping={
            "permissions": json.dumps(permissions),
            "status": "active",
            "registered_at": str(asyncio.get_event_loop().time())
        })
        
        logger.info("Agent registered", agent_id=agent_id, permissions=permissions)
        
        return {
            "status": "success",
            "token": token,
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error("Agent registration failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/message/send")
async def send_secure_message(message_data: dict, current_agent=Depends(get_current_agent)):
    """Send encrypted message through secure channel"""
    try:
        sender_id = current_agent["agent_id"]
        receiver_id = message_data["receiver_id"]
        content = message_data["content"]
        
        # Create secure message
        secure_msg = SecureMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_data.get("type", "text")
        )
        
        # Encrypt message
        encrypted_content = message_encryption.encrypt_message(content, receiver_id)
        
        # Check for threats
        threat_score = await threat_monitor.analyze_message(secure_msg)
        
        if threat_score > 0.8:
            logger.warning("High threat score detected", 
                         sender=sender_id, 
                         receiver=receiver_id, 
                         score=threat_score)
            await redis_client.lpush("security_alerts", json.dumps({
                "type": "high_threat_message",
                "sender": sender_id,
                "receiver": receiver_id,
                "threat_score": threat_score,
                "timestamp": asyncio.get_event_loop().time()
            }))
        
        # Store in message queue
        message_payload = {
            "id": secure_msg.id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "encrypted_content": encrypted_content,
            "timestamp": secure_msg.timestamp.isoformat(),
            "threat_score": threat_score
        }
        
        await redis_client.lpush(f"messages:{receiver_id}", json.dumps(message_payload))
        
        # Audit log
        await redis_client.lpush("audit_log", json.dumps({
            "action": "message_sent",
            "sender": sender_id,
            "receiver": receiver_id,
            "message_id": secure_msg.id,
            "timestamp": secure_msg.timestamp.isoformat(),
            "threat_score": threat_score
        }))
        
        # Notify receiver if connected
        if receiver_id in active_connections:
            await active_connections[receiver_id].send_text(json.dumps({
                "type": "new_message",
                "message": message_payload
            }))
        
        logger.info("Message sent successfully", 
                   sender=sender_id, 
                   receiver=receiver_id, 
                   message_id=secure_msg.id)
        
        return {
            "status": "success",
            "message_id": secure_msg.id,
            "threat_score": threat_score
        }
        
    except Exception as e:
        logger.error("Message sending failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/messages/receive")
async def receive_messages(current_agent=Depends(get_current_agent)):
    """Receive and decrypt messages for current agent"""
    try:
        agent_id = current_agent["agent_id"]
        
        # Get messages from queue
        messages = []
        while True:
            msg_data = await redis_client.rpop(f"messages:{agent_id}")
            if not msg_data:
                break
            
            message = json.loads(msg_data)
            
            # Decrypt content
            decrypted_content = message_encryption.decrypt_message(
                message["encrypted_content"], 
                agent_id
            )
            
            message["content"] = decrypted_content
            del message["encrypted_content"]
            messages.append(message)
        
        logger.info("Messages retrieved", agent_id=agent_id, count=len(messages))
        
        return {
            "status": "success",
            "messages": messages
        }
        
    except Exception as e:
        logger.error("Message retrieval failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/security/dashboard")
async def get_security_dashboard(current_agent=Depends(get_current_agent)):
    """Get security monitoring dashboard data"""
    try:
        # Get recent alerts
        alerts = []
        for i in range(10):
            alert_data = await redis_client.lindex("security_alerts", i)
            if alert_data:
                alerts.append(json.loads(alert_data))
        
        # Get audit log entries
        audit_entries = []
        for i in range(20):
            entry_data = await redis_client.lindex("audit_log", i)
            if entry_data:
                audit_entries.append(json.loads(entry_data))
        
        # Get active agents count
        active_agents = len(await redis_client.keys("agent:*"))
        
        # Calculate threat statistics
        threat_stats = await threat_monitor.get_statistics()
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "audit_log": audit_entries,
                "active_agents": active_agents,
                "threat_statistics": threat_stats,
                "system_health": "healthy"
            }
        }
        
    except Exception as e:
        logger.error("Dashboard data retrieval failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    active_connections[agent_id] = websocket
    logger.info("WebSocket connected", agent_id=agent_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time communication
            message = json.loads(data)
            logger.info("WebSocket message received", agent_id=agent_id, type=message.get("type"))
            
    except WebSocketDisconnect:
        del active_connections[agent_id]
        logger.info("WebSocket disconnected", agent_id=agent_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
