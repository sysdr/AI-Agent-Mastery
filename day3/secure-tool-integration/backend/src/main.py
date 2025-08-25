"""
Secure Tool Integration API Server
"""
import os
import sys
import structlog
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from agents.file_agent import SecureFileAgent
from security.permission_manager import PermissionManager
from security.audit_logger import AuditLogger
from tools.tool_registry import ToolRegistry

# Configure structured logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Secure Tool Integration API")
    await permission_manager.initialize()
    await audit_logger.initialize()
    await tool_registry.initialize()
    yield
    # Shutdown
    logger.info("Shutting down Secure Tool Integration API")

app = FastAPI(title="Secure Tool Integration API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Initialize components
permission_manager = PermissionManager()
audit_logger = AuditLogger()
tool_registry = ToolRegistry(permission_manager, audit_logger)
file_agent = SecureFileAgent(tool_registry, permission_manager, audit_logger)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "secure-tool-integration"}

@app.post("/agent/execute")
async def execute_agent_command(request: dict):
    """Execute agent command with security validation"""
    try:
        command = request.get("command")
        parameters = request.get("parameters", {})
        
        result = await file_agent.execute_command(command, parameters)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("Command execution failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agent/capabilities")
async def get_agent_capabilities():
    """Get available agent capabilities"""
    capabilities = await file_agent.get_capabilities()
    return {"capabilities": capabilities}

@app.get("/security/permissions")
async def get_permissions():
    """Get current permission policies"""
    permissions = await permission_manager.get_all_permissions()
    return {"permissions": permissions}

@app.get("/security/audit")
async def get_audit_logs():
    """Get recent audit logs"""
    logs = await audit_logger.get_recent_logs(limit=100)
    return {"logs": logs}

@app.get("/tools/registry")
async def get_tool_registry():
    """Get registered tools and their capabilities"""
    tools = await tool_registry.get_all_tools()
    return {"tools": tools}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
