from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import time
from ..services.conversation_manager import ConversationManager
from ..services.compliance_validator import ComplianceValidator
from ..services.personality_monitor import PersonalityMonitor
from ..services.metrics_service import metrics_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
conversation_manager = ConversationManager()
compliance_validator = ComplianceValidator()
personality_monitor = PersonalityMonitor()

class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    compliance_score: float
    personality_consistent: bool
    escalated: bool
    timestamp: str

@router.get("/sessions")
async def get_active_sessions():
    """Get list of active conversation sessions"""
    return {"sessions": list(metrics_service.active_sessions), "total": len(metrics_service.active_sessions)}

@router.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    history = metrics_service.session_history.get(session_id, [])
    return {"session_id": session_id, "messages": history}

@router.post("/validate")
async def validate_message(request: ConversationRequest):
    """Validate a message without processing"""
    start_time = time.time()
    
    try:
        compliance_result = await compliance_validator.validate_message(request.message)
        
        # Track metrics
        metrics_service.track_message(
            request.session_id or "validation", 
            request.message, 
            compliance_result
        )
        
        response_time = (time.time() - start_time) * 1000
        metrics_service.track_response_time(response_time)
        
        return {
            "is_valid": compliance_result["is_valid"],
            "score": compliance_result["score"],
            "flags": compliance_result["flags"],
            "violations": compliance_result["violations"]
        }
    except Exception as e:
        metrics_service.track_error()
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_message(request: ConversationRequest):
    """Process a message through the conversation manager"""
    start_time = time.time()
    
    try:
        # Process through conversation manager
        result = await conversation_manager.process_message(
            session_id=request.session_id or "default",
            message=request.message,
            user_id=request.user_id,
            compliance_validator=compliance_validator,
            personality_monitor=personality_monitor
        )
        
        # Track metrics
        metrics_service.track_message(
            request.session_id or "default", 
            request.message, 
            result.get("compliance_result", {"is_valid": True, "score": 1.0})
        )
        
        if "personality_result" in result:
            metrics_service.track_personality_result(
                request.session_id or "default",
                result["personality_result"]
            )
        
        response_time = (time.time() - start_time) * 1000
        metrics_service.track_response_time(response_time)
        
        return {
            "conversation_id": result.get("conversation_id", "unknown"),
            "response": result.get("response", "No response generated"),
            "compliance_score": result.get("compliance_score", 1.0),
            "personality_consistent": result.get("personality_consistent", True),
            "escalated": result.get("escalated", False),
            "timestamp": result.get("timestamp", "unknown")
        }
    except Exception as e:
        metrics_service.track_error()
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
