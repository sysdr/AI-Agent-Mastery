from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import uvicorn

from agent.core import AgentCore
from utils.logger import get_logger

# Global agent instance
agent_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    # Startup
    agent_instance = AgentCore()
    await agent_instance.initialize()
    logger.info("API server started with agent")
    yield
    # Shutdown
    if agent_instance:
        await agent_instance.cleanup()
    logger.info("API server shutdown complete")

app = FastAPI(title="Enterprise Agent API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger(__name__)

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    request_id: str
    response: str
    status: str
    timestamp: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not agent_instance or not agent_instance.is_running:
        raise HTTPException(status_code=503, detail="Agent not available")
    
    result = await agent_instance.process_request(request.message, request.context)
    return ChatResponse(**result)

@app.get("/status")
async def get_status():
    if not agent_instance:
        return {"status": "not_initialized"}
    return await agent_instance.get_status()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "enterprise-agent-api"}

@app.post("/demo")
async def run_demo():
    """Run demo functionality to populate metrics and test the system"""
    import random
    import time
    from datetime import datetime
    
    try:
        # Simulate some demo requests and responses
        demo_responses = [
            "Demo: Processing enterprise workflow analysis...",
            "Demo: Analyzing customer support tickets...", 
            "Demo: Generating business intelligence report...",
            "Demo: Optimizing resource allocation...",
            "Demo: Processing compliance audit..."
        ]
        
        # Create demo metrics
        demo_metrics = {
            "requests_processed": random.randint(15, 50),
            "success_rate": round(random.uniform(0.85, 0.99), 2),
            "avg_response_time": round(random.uniform(0.2, 1.5), 2),
            "active_sessions": random.randint(3, 12),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = random.choice(demo_responses)
        
        return {
            "status": "success",
            "message": "Demo executed successfully",
            "demo_response": response,
            "metrics": demo_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Demo execution failed", error=str(e))
        return {
            "status": "error", 
            "message": f"Demo failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/demo/metrics")
async def get_demo_metrics():
    """Get demo metrics for dashboard display"""
    import random
    from datetime import datetime, timedelta
    
    # Generate sample metrics for the last hour
    metrics = []
    now = datetime.utcnow()
    
    for i in range(12):  # 12 data points for the last hour
        timestamp = now - timedelta(minutes=i*5)
        metrics.append({
            "timestamp": timestamp.isoformat(),
            "request_count": random.randint(5, 25),
            "response_time": round(random.uniform(0.1, 2.0), 2),
            "success_rate": round(random.uniform(0.8, 1.0), 2),
            "active_users": random.randint(1, 8)
        })
    
    return {
        "status": "success",
        "metrics": metrics[::-1],  # Reverse to get chronological order
        "summary": {
            "total_requests": sum(m["request_count"] for m in metrics),
            "avg_response_time": round(sum(m["response_time"] for m in metrics) / len(metrics), 2),
            "avg_success_rate": round(sum(m["success_rate"] for m in metrics) / len(metrics), 2)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
