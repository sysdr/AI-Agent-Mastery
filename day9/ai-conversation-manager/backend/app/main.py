from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from typing import Dict, Set
import json
import asyncio
import uuid

from .services.conversation_manager import ConversationManager
from .services.compliance_validator import ComplianceValidator
from .services.personality_monitor import PersonalityMonitor
from .middleware.rate_limiter import RateLimiterMiddleware
from .routers import conversation, monitoring
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Conversation Manager",
    description="Advanced conversation management with compliance and monitoring",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware)

# Initialize services
conversation_manager = ConversationManager()
compliance_validator = ComplianceValidator()
personality_monitor = PersonalityMonitor()

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Include routers
app.include_router(conversation.router, prefix="/api/conversation")
app.include_router(monitoring.router, prefix="/api/monitoring")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through conversation manager
            response = await conversation_manager.process_message(
                session_id=session_id,
                message=message_data["message"],
                user_id=message_data.get("user_id", "anonymous"),
                compliance_validator=compliance_validator,
                personality_monitor=personality_monitor
            )
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1000)

@app.get("/")
async def root():
    return {"message": "AI Conversation Manager API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": "operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
