#!/usr/bin/env python3
"""
Simplified Multi-Modal Chat Agent - Main Application
Day 14: Production Integration & Monitoring
"""

import asyncio
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from pydantic import BaseModel

# Simple models
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    conversation_id: str
    tokens_used: int
    model_used: str
    timestamp: float = None

class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_connections: int
    requests_per_minute: int
    avg_response_time: float
    error_rate: float

# Simple MultiModal Agent
class SimpleMultiModalAgent:
    def __init__(self):
        self.conversations = {}
        
    async def process_message(
        self, 
        content: str, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        """Process text message with simple response"""
        try:
            # Simple response generation
            response_content = f"I received your message: '{content}'. This is a demo response from the Multi-Modal Chat Agent. The system is working correctly!"
            
            # Count tokens (approximation)
            tokens_used = len(content.split()) + len(response_content.split())
            
            conv_id = conversation_id or f"conv_{user_id}_{asyncio.get_event_loop().time()}"
            
            return ChatResponse(
                content=response_content,
                conversation_id=conv_id,
                tokens_used=tokens_used,
                model_used="demo-model",
                timestamp=asyncio.get_event_loop().time()
            )
            
        except Exception as e:
            return ChatResponse(
                content=f"Error processing message: {str(e)}",
                conversation_id=conversation_id or "error",
                tokens_used=0,
                model_used="error-model",
                timestamp=asyncio.get_event_loop().time()
            )

    async def process_file_message(
        self,
        file,
        message: str,
        user_id: str
    ) -> ChatResponse:
        """Process file upload with simple response"""
        try:
            file_content = await file.read()
            file_type = file.content_type
            
            response_content = f"I received your file '{file.filename}' ({file_type}) with message: '{message}'. File processing is working correctly!"
            
            tokens_used = len(message.split()) + len(response_content.split()) + 100
            
            return ChatResponse(
                content=response_content,
                conversation_id=f"file_{user_id}_{asyncio.get_event_loop().time()}",
                tokens_used=tokens_used,
                model_used="demo-file-model",
                timestamp=asyncio.get_event_loop().time()
            )
            
        except Exception as e:
            return ChatResponse(
                content=f"Error processing file: {str(e)}",
                conversation_id="error",
                tokens_used=0,
                model_used="error-model",
                timestamp=asyncio.get_event_loop().time()
            )

# Simple Auth Manager
class SimpleAuthManager:
    async def verify_token(self, token: str):
        """Simple token verification for demo"""
        return {
            "id": "demo_user",
            "username": "demo_user",
            "is_admin": True
        }

# Simple Input Validator
class SimpleInputValidator:
    async def validate_chat_input(self, content: str) -> bool:
        """Simple input validation"""
        return bool(content and len(content) < 10000)
    
    async def validate_file_upload(self, file) -> bool:
        """Simple file validation"""
        return bool(file and file.size < 10485760)  # 10MB limit

# Create FastAPI application
app = FastAPI(
    title="Multi-Modal Chat Agent",
    description="Production-grade chat agent with monitoring and security",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize components
multimodal_agent = SimpleMultiModalAgent()
auth_manager = SimpleAuthManager()
validator = SimpleInputValidator()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@app.get("/metrics")
async def get_metrics():
    """Simple metrics endpoint"""
    return {
        "cpu_usage": 25.5,
        "memory_usage": 60.2,
        "active_connections": 5,
        "requests_per_minute": 120,
        "avg_response_time": 0.3,
        "error_rate": 0.01
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    token: str = Depends(security)
):
    """Main chat endpoint"""
    try:
        # Authenticate user
        user = await auth_manager.verify_token(token.credentials)
        
        # Validate input
        if not await validator.validate_chat_input(message.content):
            raise HTTPException(status_code=400, detail="Invalid input detected")
        
        # Process with agent
        response = await multimodal_agent.process_message(
            content=message.content,
            user_id=user["id"],
            conversation_id=message.conversation_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/chat/upload")
async def upload_and_chat(
    file: UploadFile = File(...),
    message: str = "",
    token: str = Depends(security)
):
    """Upload file and chat endpoint"""
    try:
        # Authenticate user
        user = await auth_manager.verify_token(token.credentials)
        
        # Validate file
        if not await validator.validate_file_upload(file):
            raise HTTPException(status_code=400, detail="Invalid file upload")
        
        # Process with multimodal agent
        response = await multimodal_agent.process_file_message(
            file=file,
            message=message,
            user_id=user["id"]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.get("/analytics/metrics")
async def get_system_metrics(token: str = Depends(security)) -> SystemMetrics:
    """Get system performance metrics"""
    user = await auth_manager.verify_token(token.credentials)
    
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return SystemMetrics(
        cpu_usage=25.5,
        memory_usage=60.2,
        active_connections=5,
        requests_per_minute=120,
        avg_response_time=0.3,
        error_rate=0.01
    )

if __name__ == "__main__":
    print("🚀 Starting Multi-Modal Chat Agent (Simplified Version)")
    print("📡 Backend will be available at: http://localhost:8000")
    print("📊 Health check: http://localhost:8000/health")
    print("📈 Metrics: http://localhost:8000/metrics")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
