from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.models import QueryRequest, ExpertResponse
from app.agents.expert_agent import ExpertAgent
from app.core.database import get_db
from config.settings import settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Expert Agent System",
    description="AI Agent Specialization & Expertise Validation System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available domains
AVAILABLE_DOMAINS = {
    "technology": "Technology and Software Development",
    "medical": "Medical and Health Information",
    "legal": "Legal and Regulatory Information",
    "finance": "Financial and Investment Information",
    "science": "Scientific Research and Data",
}

@app.get("/")
async def root():
    return {"message": "Expert Agent System API", "version": "1.0.0"}

@app.get("/domains")
async def get_available_domains():
    return {"domains": AVAILABLE_DOMAINS}

@app.post("/query/{domain}")
async def process_expert_query(
    domain: str,
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    if domain not in AVAILABLE_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Domain '{domain}' not supported")
    
    try:
        expert_agent = ExpertAgent(domain, db)
        result = await expert_agent.process_query(
            request.query,
            request.required_confidence or settings.min_confidence_threshold
        )
        
        return result
        
    except Exception as e:
        logger.error("Query processing failed", domain=domain, query=request.query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/audit/{query_id}")
async def get_audit_trail(query_id: str, db: Session = Depends(get_db)):
    from app.core.models import AuditLog
    
    audit_log = db.query(AuditLog).filter(AuditLog.query_id == query_id).first()
    
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit trail not found")
    
    return {
        "query_id": audit_log.query_id,
        "query": audit_log.query_text,
        "response": audit_log.response_text,
        "confidence_score": audit_log.confidence_score,
        "validation_steps": audit_log.validation_steps,
        "processing_time": audit_log.processing_time,
        "timestamp": audit_log.timestamp
    }

@app.get("/stats/{domain}")
async def get_domain_stats(domain: str, db: Session = Depends(get_db)):
    if domain not in AVAILABLE_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Domain '{domain}' not supported")
    
    from app.knowledge.knowledge_manager import KnowledgeManager
    
    knowledge_manager = KnowledgeManager(db)
    stats = knowledge_manager.get_domain_expertise_stats(domain)
    
    return stats

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "domains": list(AVAILABLE_DOMAINS.keys()),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
