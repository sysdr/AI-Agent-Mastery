from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from models.conversation import Conversation, Message, AuditLog
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get security and performance metrics for dashboard"""
    
    # Conversation metrics
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    active_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.is_active == True
    ).scalar()
    
    # Message metrics
    total_messages = db.query(func.count(Message.id)).scalar()
    pii_messages = db.query(func.count(Message.id)).filter(
        Message.pii_detected == True
    ).scalar()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= yesterday
    ).scalar()
    
    recent_messages = db.query(func.count(Message.id)).filter(
        Message.created_at >= yesterday
    ).scalar()
    
    # Security events
    security_events = db.query(AuditLog).filter(
        AuditLog.security_level.in_(["WARNING", "CRITICAL"]),
        AuditLog.timestamp >= yesterday
    ).count()
    
    # Token usage
    total_tokens = db.query(func.sum(Message.token_count)).scalar() or 0
    
    return {
        "conversations": {
            "total": total_conversations,
            "active": active_conversations,
            "recent_24h": recent_conversations
        },
        "messages": {
            "total": total_messages,
            "pii_detected": pii_messages,
            "recent_24h": recent_messages,
            "pii_percentage": (pii_messages / total_messages * 100) if total_messages > 0 else 0
        },
        "security": {
            "events_24h": security_events,
            "pii_detection_rate": (pii_messages / total_messages * 100) if total_messages > 0 else 0
        },
        "performance": {
            "total_tokens": total_tokens,
            "avg_tokens_per_message": total_tokens / total_messages if total_messages > 0 else 0
        }
    }

@router.get("/security-events")
async def get_security_events(
    limit: int = 50,
    security_level: str = None,
    db: Session = Depends(get_db)
):
    """Get recent security audit events"""
    
    query = db.query(AuditLog)
    
    if security_level:
        query = query.filter(AuditLog.security_level == security_level)
    
    events = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return {
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "security_level": event.security_level,
                "timestamp": event.timestamp,
                "event_data": event.event_data
            }
            for event in events
        ]
    }
