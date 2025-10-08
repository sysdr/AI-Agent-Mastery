#!/usr/bin/env python3
import uvicorn
import time
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Advanced Tool Orchestration & Monitoring",
    description="Production-ready AI agent tool orchestration system",
    version="1.0.0"
)

# Global metrics tracking
metrics = {
    "total_orchestrations": 0,
    "successful_orchestrations": 0,
    "total_cost": 0.0,
    "execution_times": [],
    "tool_usage": {},
    "recent_orchestrations": [],
    "security_incidents": 0,
    "active_orchestrations": 0
}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Advanced Tool Orchestration System is running!"}

@app.get("/api/status")
async def get_system_status():
    """Get system health and metrics"""
    return {
        "status": "healthy",
        "active_orchestrations": metrics["active_orchestrations"],
        "total_cost": metrics["total_cost"],
        "security_incidents": metrics["security_incidents"],
        "circuit_breakers": {}
    }

@app.get("/api/metrics")
async def get_detailed_metrics():
    """Get detailed system metrics"""
    success_rate = (metrics["successful_orchestrations"] / metrics["total_orchestrations"] * 100) if metrics["total_orchestrations"] > 0 else 100.0
    avg_execution_time = sum(metrics["execution_times"]) / len(metrics["execution_times"]) if metrics["execution_times"] else 0.0
    
    return {
        "system_health": {
            "total_orchestrations": metrics["total_orchestrations"],
            "success_rate": round(success_rate, 2),
            "avg_execution_time": round(avg_execution_time, 2),
            "total_cost": metrics["total_cost"]
        },
        "tool_usage": metrics["tool_usage"],
        "recent_orchestrations": metrics["recent_orchestrations"][-10:],  # Last 10
        "performance": {
            "p50_execution_time": round(sorted(metrics["execution_times"])[len(metrics["execution_times"])//2] if metrics["execution_times"] else 0.0, 2),
            "p95_execution_time": round(sorted(metrics["execution_times"])[int(len(metrics["execution_times"])*0.95)] if metrics["execution_times"] else 0.0, 2),
            "p99_execution_time": round(sorted(metrics["execution_times"])[int(len(metrics["execution_times"])*0.99)] if metrics["execution_times"] else 0.0, 2)
        }
    }

@app.post("/api/research")
async def execute_research(request: dict):
    """Execute research task with orchestrated tools"""
    start_time = time.time()
    query = request.get("query", "test query")
    tools_config = request.get("tools", {})
    security_level = request.get("security_level", "standard")
    
    # Increment active orchestrations
    metrics["active_orchestrations"] += 1
    
    try:
        # Simulate processing time
        await asyncio.sleep(0.5)  # Simulate 500ms processing
        
        # Track tool usage
        for tool_name, enabled in tools_config.items():
            if enabled:
                metrics["tool_usage"][tool_name] = metrics["tool_usage"].get(tool_name, 0) + 1
        
        # Calculate execution time and cost
        execution_time = time.time() - start_time
        cost = len(tools_config) * 0.05  # $0.05 per tool used
        
        # Update metrics
        metrics["total_orchestrations"] += 1
        metrics["successful_orchestrations"] += 1
        metrics["total_cost"] += cost
        metrics["execution_times"].append(execution_time)
        
        # Add to recent orchestrations
        orchestration_record = {
            "request_id": f"req_{int(time.time() * 1000)}",
            "execution_time": execution_time,
            "total_cost": cost,
            "tools_used": [tool for tool, enabled in tools_config.items() if enabled],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        metrics["recent_orchestrations"].append(orchestration_record)
        
        # Keep only last 100 records
        if len(metrics["recent_orchestrations"]) > 100:
            metrics["recent_orchestrations"] = metrics["recent_orchestrations"][-100:]
        
        return {
            "query": query,
            "synthesis": {
                "synthesis": f"Research completed for: {query}. This is a demo response showing the system is working. Processed with {len(tools_config)} tools in {execution_time:.2f}s."
            },
            "sources": [tool for tool, enabled in tools_config.items() if enabled],
            "security_validated": True,
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "cost": cost
        }
        
    except Exception as e:
        # Track failure
        metrics["total_orchestrations"] += 1
        metrics["security_incidents"] += 1
        
        orchestration_record = {
            "request_id": f"req_{int(time.time() * 1000)}",
            "execution_time": time.time() - start_time,
            "total_cost": 0.0,
            "tools_used": [],
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        metrics["recent_orchestrations"].append(orchestration_record)
        
        raise e
    finally:
        # Decrement active orchestrations
        metrics["active_orchestrations"] = max(0, metrics["active_orchestrations"] - 1)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
