from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.models import KnowledgeBase, ValidationStatus
import structlog

logger = structlog.get_logger()

class KnowledgeManager:
    def __init__(self, db: Session):
        self.db = db
    
    def search_knowledge(self, query: str, domain: str, limit: int = 10) -> List[KnowledgeBase]:
        """Search knowledge base for relevant entries"""
        query_words = query.lower().split()
        
        # Build search filters
        filters = []
        filters.append(KnowledgeBase.domain == domain)
        filters.append(KnowledgeBase.validation_status == ValidationStatus.VALIDATED)
        
        # Add content search
        for word in query_words:
            filters.append(or_(
                KnowledgeBase.content.contains(word),
                KnowledgeBase.topic.contains(word)
            ))
        
        results = self.db.query(KnowledgeBase).filter(
            and_(*filters)
        ).order_by(
            KnowledgeBase.confidence_score.desc(),
            KnowledgeBase.access_count.desc()
        ).limit(limit).all()
        
        # Update access counts
        for entry in results:
            entry.access_count += 1
        
        self.db.commit()
        
        return results
    
    def add_knowledge(self, domain: str, topic: str, content: str, 
                     sources: List[str], confidence: float) -> KnowledgeBase:
        """Add new knowledge entry"""
        knowledge = KnowledgeBase(
            domain=domain,
            topic=topic,
            content=content,
            sources=sources,
            confidence_score=confidence,
            validation_status=ValidationStatus.PENDING
        )
        
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        
        logger.info("Knowledge added", id=knowledge.id, domain=domain, topic=topic)
        return knowledge
    
    def update_knowledge_accuracy(self, knowledge_id: int, accuracy_score: float):
        """Update accuracy score based on validation results"""
        knowledge = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_id
        ).first()
        
        if knowledge:
            knowledge.accuracy_score = accuracy_score
            
            # Update validation status based on accuracy
            if accuracy_score >= 0.8:
                knowledge.validation_status = ValidationStatus.VALIDATED
            elif accuracy_score < 0.3:
                knowledge.validation_status = ValidationStatus.DISPUTED
            
            self.db.commit()
    
    def get_domain_expertise_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics about domain expertise"""
        total_entries = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.domain == domain
        ).count()
        
        validated_entries = self.db.query(KnowledgeBase).filter(
            and_(
                KnowledgeBase.domain == domain,
                KnowledgeBase.validation_status == ValidationStatus.VALIDATED
            )
        ).count()
        
        avg_confidence = self.db.query(KnowledgeBase.confidence_score).filter(
            and_(
                KnowledgeBase.domain == domain,
                KnowledgeBase.validation_status == ValidationStatus.VALIDATED
            )
        ).all()
        
        avg_conf_score = sum(score[0] for score in avg_confidence) / len(avg_confidence) if avg_confidence else 0.0
        
        return {
            "domain": domain,
            "total_entries": total_entries,
            "validated_entries": validated_entries,
            "validation_rate": validated_entries / total_entries if total_entries > 0 else 0.0,
            "average_confidence": avg_conf_score
        }
    
    def cleanup_expired_knowledge(self, retention_days: int = 90):
        """Remove or mark expired knowledge entries"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        expired_entries = self.db.query(KnowledgeBase).filter(
            and_(
                KnowledgeBase.updated_at < cutoff_date,
                KnowledgeBase.access_count == 0
            )
        ).all()
        
        for entry in expired_entries:
            entry.validation_status = ValidationStatus.EXPIRED
        
        self.db.commit()
        
        logger.info("Knowledge cleanup completed", expired_count=len(expired_entries))
        return len(expired_entries)
