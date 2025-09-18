from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy.orm import Session

from models.database import SessionLocal, Base, engine, Agent
from agents.base_agent import BaseAgent
from agents.content_agents import WriterAgent, EditorAgent, ReviewerAgent, CoordinatorAgent
from security.auth import AgentSecurity, CapabilityChecker
from security.quota import QuotaManager

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Agent Security System",
    description="Secure content creation system with role-based AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
agent_security = AgentSecurity()
quota_manager = QuotaManager()

# Pydantic models
class AgentCreate(BaseModel):
    name: str
    agent_type: str  # writer, editor, reviewer, coordinator

class ContentCreate(BaseModel):
    title: str
    topic: str
    length: int = 500

class TaskAssign(BaseModel):
    topic: str
    priority: str = "normal"

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Agent factory
def get_agent_instance(agent_id: int, agent_type: str) -> BaseAgent:
    agent_classes = {
        "writer": WriterAgent,
        "editor": EditorAgent,
        "reviewer": ReviewerAgent,
        "coordinator": CoordinatorAgent
    }
    return agent_classes.get(agent_type, BaseAgent)(agent_id)

@app.post("/agents", response_model=Dict[str, Any])
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent with security credentials"""
    
    # Generate key pair for agent
    private_key, public_key = agent_security.generate_agent_keypair()
    capabilities = CapabilityChecker.get_capabilities(agent_data.agent_type)
    
    # Create agent in database
    agent = Agent(
        name=agent_data.name,
        agent_type=agent_data.agent_type,
        capabilities=capabilities,
        certificate=public_key,
        private_key=private_key,
        status="active"
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Generate capability token
    token = agent_security.create_capability_token(agent.id, capabilities)
    
    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "capabilities": capabilities,
        "token": token,
        "status": agent.status
    }

@app.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents(db: Session = Depends(get_db)):
    """List all agents with their current status"""
    agents = db.query(Agent).all()
    
    result = []
    for agent in agents:
        # Get usage stats
        usage_stats = await quota_manager.get_usage_stats(agent.id)
        
        result.append({
            "id": agent.id,
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status,
            "capabilities": agent.capabilities,
            "usage_stats": usage_stats,
            "created_at": agent.created_at.isoformat()
        })
    
    return result

@app.post("/content/create")
async def create_content(content_data: ContentCreate, db: Session = Depends(get_db)):
    """Create content using writer agent"""
    
    # Find an active writer agent
    writer = db.query(Agent).filter(
        Agent.agent_type == "writer",
        Agent.status == "active"
    ).first()
    
    if not writer:
        raise HTTPException(status_code=404, detail="No active writer agent found")
    
    writer_agent = WriterAgent(writer.id)
    result = await writer_agent.create_content(
        content_data.title,
        content_data.topic,
        content_data.length
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Content creation failed")
    
    return result

@app.post("/content/{content_id}/review")
async def review_content(content_id: int, db: Session = Depends(get_db)):
    """Review content using editor agent"""
    
    # Find an active editor agent
    editor = db.query(Agent).filter(
        Agent.agent_type == "editor",
        Agent.status == "active"
    ).first()
    
    if not editor:
        raise HTTPException(status_code=404, detail="No active editor agent found")
    
    editor_agent = EditorAgent(editor.id)
    result = await editor_agent.review_content(content_id)
    
    if not result:
        raise HTTPException(status_code=400, detail="Content review failed")
    
    return result

@app.post("/content/{content_id}/final-review")
async def final_review_content(content_id: int, db: Session = Depends(get_db)):
    """Final review content using reviewer agent"""
    
    # Find an active reviewer agent
    reviewer = db.query(Agent).filter(
        Agent.agent_type == "reviewer",
        Agent.status == "active"
    ).first()
    
    if not reviewer:
        raise HTTPException(status_code=404, detail="No active reviewer agent found")
    
    reviewer_agent = ReviewerAgent(reviewer.id)
    result = await reviewer_agent.final_review(content_id)
    
    if not result:
        raise HTTPException(status_code=400, detail="Final review failed")
    
    return result

@app.post("/tasks/assign")
async def assign_task(task_data: TaskAssign, db: Session = Depends(get_db)):
    """Assign content creation task using coordinator agent"""
    
    # Find an active coordinator agent
    coordinator = db.query(Agent).filter(
        Agent.agent_type == "coordinator",
        Agent.status == "active"
    ).first()
    
    if not coordinator:
        raise HTTPException(status_code=404, detail="No active coordinator agent found")
    
    coordinator_agent = CoordinatorAgent(coordinator.id)
    result = await coordinator_agent.assign_content_task(
        task_data.topic,
        task_data.priority
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Task assignment failed")
    
    return result

@app.get("/agents/{agent_id}/messages")
async def get_agent_messages(agent_id: int, db: Session = Depends(get_db)):
    """Get messages for specific agent"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_instance = get_agent_instance(agent_id, agent.agent_type)
    messages = await agent_instance.receive_messages()
    
    return {"messages": messages}

@app.get("/agents/{agent_id}/usage")
async def get_agent_usage(agent_id: int, db: Session = Depends(get_db)):
    """Get usage statistics for agent"""
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    usage_stats = await quota_manager.get_usage_stats(agent_id)
    return usage_stats

@app.get("/system/status")
async def system_status():
    """Get overall system status"""
    return {
        "status": "operational",
        "security": "active",
        "encryption": "enabled",
        "quota_management": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
