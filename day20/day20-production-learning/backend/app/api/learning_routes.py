from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import redis
from ..services.learning_service import ProductionLearningService
from ..models.learning import FeedbackData
from ..utils.database import get_database
from sqlalchemy.orm import Session

router = APIRouter()
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
learning_service = ProductionLearningService(redis_client)

class FeedbackRequest(BaseModel):
    user_id: str
    agent_response_id: str
    satisfaction_score: float
    feedback_text: Optional[str] = None
    demographic_data: Optional[Dict[str, Any]] = None

class ExplainabilityRequest(BaseModel):
    input_data: Dict[str, Any]
    model_version: Optional[str] = "current"

@router.post("/feedback")
async def submit_feedback(
    feedback_request: FeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_database)
):
    """Submit user feedback for online learning"""
    try:
        # Store feedback in database
        feedback_data = FeedbackData(
            user_id=feedback_request.user_id,
            agent_response_id=feedback_request.agent_response_id,
            satisfaction_score=feedback_request.satisfaction_score,
            feedback_text=feedback_request.feedback_text,
            demographic_data=feedback_request.demographic_data,
            privacy_level="standard"
        )
        
        db.add(feedback_data)
        db.commit()
        
        # Process feedback asynchronously
        background_tasks.add_task(
            learning_service.process_feedback, 
            feedback_request.dict()
        )
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_data.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/bias")
async def get_bias_metrics(
    hours: int = 24,
    db: Session = Depends(get_database)
):
    """Get bias detection metrics"""
    try:
        from ..models.learning import BiasMetric
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = db.query(BiasMetric).filter(
            BiasMetric.created_at > cutoff_time
        ).all()
        
        return {
            "total_checks": len(metrics),
            "bias_detected": sum(1 for m in metrics if m.threshold_exceeded),
            "metrics": [
                {
                    "attribute": m.protected_attribute,
                    "metric_type": m.metric_type,
                    "value": m.metric_value,
                    "threshold_exceeded": m.threshold_exceeded,
                    "timestamp": m.created_at.isoformat()
                }
                for m in metrics
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/performance")
async def get_performance_metrics(
    hours: int = 24,
    db: Session = Depends(get_database)
):
    """Get system performance metrics"""
    try:
        from ..models.learning import PerformanceMetric
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = db.query(PerformanceMetric).filter(
            PerformanceMetric.created_at > cutoff_time
        ).all()
        
        if not metrics:
            return {"message": "No performance data available"}
        
        avg_response_time = sum(m.response_time_ms for m in metrics) / len(metrics)
        total_cost = sum(m.api_cost_usd for m in metrics)
        avg_accuracy = sum(m.accuracy_score for m in metrics) / len(metrics)
        
        return {
            "time_period_hours": hours,
            "total_requests": len(metrics),
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_cost_usd": round(total_cost, 4),
            "avg_accuracy": round(avg_accuracy, 3),
            "cost_per_request": round(total_cost / len(metrics), 4) if metrics else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_decision(request: ExplainabilityRequest):
    """Get explanation for AI agent decision"""
    try:
        explanation = await learning_service.get_model_explanation(
            request.input_data
        )
        
        return {
            "status": "success",
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "production-learning",
        "timestamp": datetime.utcnow().isoformat()
    }
