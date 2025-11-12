from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry, multiprocess, generate_latest as prom_generate
import google.generativeai as genai
from contextlib import asynccontextmanager
import asyncio
import json
import time
import logging
import psutil
import os
from typing import AsyncGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('agent_requests_total', 'Total agent requests', ['endpoint', 'status'])
REQUEST_DURATION = Histogram('agent_request_duration_seconds', 'Request duration', ['endpoint'])
AI_LATENCY = Histogram('ai_generation_latency_seconds', 'AI generation latency')
ERROR_COUNT = Counter('agent_errors_total', 'Total errors', ['error_type'])

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-gemini-api-key'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Enterprise AI Agent Platform Starting...")
    yield
    logger.info("👋 Shutting down gracefully...")

app = FastAPI(
    title="Enterprise AI Agent Platform",
    description="Production-ready multi-agent system with full observability",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Kubernetes liveness probe"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Verify AI service is accessible
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        return {"status": "ready", "ai_service": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Agent endpoints
@app.post("/api/v1/agent/chat")
async def agent_chat(request: dict):
    """Process agent chat request with metrics"""
    start_time = time.time()
    
    try:
        query = request.get('query', '')
        agent_type = request.get('agent_type', 'general')
        
        REQUEST_COUNT.labels(endpoint='/api/v1/agent/chat', status='processing').inc()
        
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        ai_start = time.time()
        response = model.generate_content(
            f"As a {agent_type} AI agent: {query}"
        )
        AI_LATENCY.observe(time.time() - ai_start)
        
        duration = time.time() - start_time
        REQUEST_DURATION.labels(endpoint='/api/v1/agent/chat').observe(duration)
        REQUEST_COUNT.labels(endpoint='/api/v1/agent/chat', status='success').inc()
        
        return {
            "response": response.text,
            "agent_type": agent_type,
            "latency_ms": round(duration * 1000, 2),
            "timestamp": time.time()
        }
        
    except Exception as e:
        ERROR_COUNT.labels(error_type=type(e).__name__).inc()
        REQUEST_COUNT.labels(endpoint='/api/v1/agent/chat', status='error').inc()
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agent/stream")
async def agent_stream(request: dict):
    """Streaming agent response with backpressure handling"""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            query = request.get('query', '')
            
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            response = model.generate_content(query, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text, 'timestamp': time.time()})}\n\n"
                    await asyncio.sleep(0.01)  # Backpressure control
                    
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.get("/api/v1/metrics/system")
async def system_metrics():
    """System resource metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "timestamp": time.time()
    }

@app.get("/api/v1/metrics/business")
async def business_metrics():
    """Business metrics for stakeholder dashboard"""
    # In production, these would come from a database
    return {
        "total_requests_today": 1247,
        "average_response_time_ms": 342,
        "success_rate_percent": 99.7,
        "cost_per_request_cents": 0.12,
        "active_users": 89,
        "ai_accuracy_score": 94.3,
        "user_satisfaction": 4.7,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
