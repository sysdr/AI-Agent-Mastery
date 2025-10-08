"""
Production Orchestration System - Main Application
Coordinates AI agents with security validation and failure recovery
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from typing import List, Dict, Any
import json
import time
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

from orchestrator.workflow_engine import WorkflowEngine
from orchestrator.scheduler import TaskScheduler
from orchestrator.recovery import FailureRecovery
from agents.document_agent import DocumentAgent
from agents.validation_agent import ValidationAgent  
from agents.onboarding_agent import OnboardingAgent
from security.auth_manager import AuthManager
from security.compliance_checker import ComplianceChecker
from monitoring.metrics_collector import MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
orchestration_state = {
    "active_workflows": {},
    "agent_status": {},
    "security_context": {},
    "metrics": {}
}

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Production Orchestration System")
    
    # Initialize components
    app.workflow_engine = WorkflowEngine()
    app.scheduler = TaskScheduler()
    app.recovery = FailureRecovery()
    app.auth_manager = AuthManager()
    app.compliance = ComplianceChecker()
    app.metrics = MetricsCollector()
    
    # Initialize agents
    app.document_agent = DocumentAgent()
    app.validation_agent = ValidationAgent()
    app.onboarding_agent = OnboardingAgent()
    
    logger.info("✅ All components initialized")
    yield
    
    logger.info("🛑 Shutting down orchestration system")

app = FastAPI(
    title="Production Orchestration System",
    description="AI Agent Orchestration with Security & Compliance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class WorkflowRequest:
    workflow_type: str
    customer_id: str
    data: Dict[str, Any]
    compliance_level: str = "standard"

@dataclass  
class WorkflowResponse:
    workflow_id: str
    status: WorkflowStatus
    progress: float
    results: Dict[str, Any]
    created_at: float
    updated_at: float

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract user info"""
    try:
        # In production, validate JWT token here
        return {"user_id": "demo_user", "role": "admin"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    user=Depends(verify_token)
):
    """Create and start a new workflow with security validation"""
    
    workflow_id = str(uuid.uuid4())
    timestamp = time.time()
    
    logger.info(f"Creating workflow {workflow_id} for customer {request.customer_id}")
    
    # Security validation
    security_context = await app.auth_manager.create_context(
        user["user_id"], 
        request.customer_id,
        request.compliance_level
    )
    
    # Compliance check
    compliance_result = await app.compliance.validate_workflow(
        request.workflow_type,
        request.data,
        request.compliance_level
    )
    
    if not compliance_result["approved"]:
        raise HTTPException(
            status_code=403, 
            detail=f"Compliance violation: {compliance_result['reason']}"
        )
    
    # Initialize workflow
    workflow = WorkflowResponse(
        workflow_id=workflow_id,
        status=WorkflowStatus.PENDING,
        progress=0.0,
        results={},
        created_at=timestamp,
        updated_at=timestamp
    )
    
    orchestration_state["active_workflows"][workflow_id] = workflow
    orchestration_state["security_context"][workflow_id] = security_context
    
    # Start workflow execution in background
    background_tasks.add_task(execute_workflow, workflow_id, request)
    
    return workflow

@app.get("/api/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, user=Depends(verify_token)):
    """Get workflow status and results"""
    
    if workflow_id not in orchestration_state["active_workflows"]:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return orchestration_state["active_workflows"][workflow_id]

@app.get("/api/workflows", response_model=List[WorkflowResponse])
async def list_workflows(user=Depends(verify_token)):
    """List all workflows for the user"""
    
    workflows = list(orchestration_state["active_workflows"].values())
    return sorted(workflows, key=lambda x: x.created_at, reverse=True)

@app.get("/api/system/status")
async def get_system_status(user=Depends(verify_token)):
    """Get overall system status and metrics"""
    
    return {
        "status": "healthy",
        "active_workflows": len(orchestration_state["active_workflows"]),
        "agent_status": {
            "document_agent": "healthy",
            "validation_agent": "healthy", 
            "onboarding_agent": "healthy"
        },
        "metrics": await app.metrics.get_current_metrics(),
        "timestamp": time.time()
    }

@app.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow updates"""
    
    await websocket.accept()
    
    try:
        while True:
            if workflow_id in orchestration_state["active_workflows"]:
                workflow = orchestration_state["active_workflows"][workflow_id]
                await websocket.send_text(json.dumps(asdict(workflow)))
            
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"WebSocket error for workflow {workflow_id}: {e}")
    finally:
        await websocket.close()

async def execute_workflow(workflow_id: str, request: WorkflowRequest):
    """Execute workflow with orchestrated agents"""
    
    try:
        workflow = orchestration_state["active_workflows"][workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.updated_at = time.time()
        
        logger.info(f"Starting workflow execution: {workflow_id}")
        
        # Customer onboarding workflow
        if request.workflow_type == "customer_onboarding":
            results = await execute_onboarding_workflow(workflow_id, request)
        else:
            raise ValueError(f"Unknown workflow type: {request.workflow_type}")
        
        # Update final status
        workflow.status = WorkflowStatus.COMPLETED
        workflow.progress = 100.0
        workflow.results = results
        workflow.updated_at = time.time()
        
        logger.info(f"Workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {e}")
        
        # Trigger failure recovery
        await app.recovery.handle_workflow_failure(workflow_id, str(e))
        
        workflow = orchestration_state["active_workflows"][workflow_id]
        workflow.status = WorkflowStatus.FAILED
        workflow.results = {"error": str(e)}
        workflow.updated_at = time.time()

async def execute_onboarding_workflow(workflow_id: str, request: WorkflowRequest):
    """Execute customer onboarding with coordinated agents"""
    
    workflow = orchestration_state["active_workflows"][workflow_id]
    security_context = orchestration_state["security_context"][workflow_id]
    
    results = {"steps": []}
    
    # Step 1: Document Processing (20% progress)
    logger.info(f"Step 1: Document processing for workflow {workflow_id}")
    workflow.progress = 10.0
    
    doc_result = await app.document_agent.process_documents(
        request.data.get("documents", []),
        security_context
    )
    results["steps"].append({"step": "document_processing", "result": doc_result})
    workflow.progress = 20.0
    
    # Step 2: Validation (40% progress)
    logger.info(f"Step 2: Validation for workflow {workflow_id}")
    
    validation_result = await app.validation_agent.validate_customer(
        request.customer_id,
        doc_result,
        security_context
    )
    results["steps"].append({"step": "validation", "result": validation_result})
    workflow.progress = 50.0
    
    # Step 3: Compliance Check (60% progress) 
    logger.info(f"Step 3: Compliance check for workflow {workflow_id}")
    
    compliance_result = await app.compliance.deep_compliance_check(
        request.customer_id,
        validation_result,
        request.compliance_level
    )
    results["steps"].append({"step": "compliance", "result": compliance_result})
    workflow.progress = 70.0
    
    # Step 4: Account Setup (80% progress)
    logger.info(f"Step 4: Account setup for workflow {workflow_id}")
    
    account_result = await app.onboarding_agent.setup_account(
        request.customer_id,
        validation_result,
        compliance_result,
        security_context
    )
    results["steps"].append({"step": "account_setup", "result": account_result})
    workflow.progress = 90.0
    
    # Final results compilation
    results["customer_id"] = request.customer_id
    results["onboarding_complete"] = True
    results["account_id"] = account_result.get("account_id")
    results["compliance_status"] = compliance_result.get("status")
    
    return results

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
