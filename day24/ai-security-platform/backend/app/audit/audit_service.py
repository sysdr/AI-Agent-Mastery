import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.models import AuditLog
import asyncio
from kafka import KafkaProducer
import structlog

logger = structlog.get_logger()

class AuditService:
    def __init__(self):
        self.producer = None
        self._initialize_kafka()
        
    def _initialize_kafka(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            logger.warning("Kafka not available, using database only", error=str(e))
    
    def create_audit_log(
        self, 
        db: Session,
        user_id: Optional[int],
        action: str,
        resource: str,
        details: Dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        # Create tamper-proof hash
        hash_data = f"{user_id or 'anonymous'}:{action}:{resource}:{json.dumps(details, sort_keys=True)}:{datetime.utcnow().isoformat()}"
        hash_signature = hashlib.sha256(hash_data.encode()).hexdigest()
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            hash_signature=hash_signature
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        # Send to Kafka for real-time processing
        if self.producer:
            try:
                self.producer.send('audit_events', {
                    'id': audit_log.id,
                    'user_id': user_id,
                    'action': action,
                    'resource': resource,
                    'timestamp': audit_log.timestamp.isoformat(),
                    'hash': hash_signature
                })
            except Exception as e:
                logger.error("Failed to send audit event to Kafka", error=str(e))
                
        return audit_log
    
    def verify_audit_integrity(self, db: Session, audit_id: int) -> bool:
        audit_log = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
        if not audit_log:
            return False
            
        # Recalculate hash
        user_id_str = str(audit_log.user_id) if audit_log.user_id else 'anonymous'
        hash_data = f"{user_id_str}:{audit_log.action}:{audit_log.resource}:{json.dumps(audit_log.details, sort_keys=True)}:{audit_log.timestamp.isoformat()}"
        calculated_hash = hashlib.sha256(hash_data.encode()).hexdigest()
        
        return calculated_hash == audit_log.hash_signature
    
    def get_audit_trail(self, db: Session, user_id: Optional[int] = None, limit: int = 100):
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

audit_service = AuditService()
