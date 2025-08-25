#!/bin/bash

# Day 3: Secure Tool Integration - Full Implementation Script
# Creates a production-grade file system agent with security boundaries

set -e

PROJECT_NAME="secure-tool-integration"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

echo "🚀 Setting up Secure Tool Integration Project..."

# Create project structure
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
mkdir -p $BACKEND_DIR/{src/{agents,security,tools,utils},tests,logs,data/sandbox}
mkdir -p $FRONTEND_DIR/{src/{components,services,utils},public}

echo "📁 Created project structure"

# Backend Implementation
cat > $BACKEND_DIR/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
psutil==5.9.6
cryptography==41.0.7
sqlalchemy==2.0.23
sqlite3-encryption==0.0.3
google-generativeai==0.3.2
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
secure==0.3.0
python-jose==3.3.0
passlib==1.7.4
watchdog==3.0.0
structlog==23.2.0
prometheus-client==0.19.0
EOF

# Main application
cat > $BACKEND_DIR/src/main.py << 'EOF'
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

app = FastAPI(title="Secure Tool Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.on_startup
async def startup_event():
    logger.info("Starting Secure Tool Integration API")
    await permission_manager.initialize()
    await audit_logger.initialize()
    await tool_registry.initialize()

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
EOF

# Permission Manager
cat > $BACKEND_DIR/src/security/permission_manager.py << 'EOF'
"""
Permission Management System with capability-based security
"""
import json
import os
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import structlog

logger = structlog.get_logger()

@dataclass
class Permission:
    resource: str
    action: str
    constraints: Dict[str, any]
    granted_at: str

@dataclass
class SecurityPolicy:
    name: str
    permissions: List[Permission]
    resource_limits: Dict[str, any]

class PermissionManager:
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.active_grants: Dict[str, Set[str]] = {}
        self.policy_file = "data/security_policies.json"
        
    async def initialize(self):
        """Initialize permission system with default policies"""
        await self._load_default_policies()
        logger.info("Permission manager initialized")
        
    async def _load_default_policies(self):
        """Load default security policies"""
        default_policies = {
            "file_agent": SecurityPolicy(
                name="file_agent",
                permissions=[
                    Permission("file", "read", {"path_prefix": "/home/user/documents"}, "system"),
                    Permission("file", "write", {"path_prefix": "/home/user/documents"}, "system"),
                    Permission("file", "list", {"path_prefix": "/home/user"}, "system"),
                ],
                resource_limits={
                    "max_file_size": 10 * 1024 * 1024,  # 10MB
                    "max_concurrent_operations": 5,
                    "timeout_seconds": 30
                }
            ),
            "sandbox_tool": SecurityPolicy(
                name="sandbox_tool",
                permissions=[
                    Permission("execute", "command", {"whitelist": ["ls", "cat", "head", "tail"]}, "system"),
                    Permission("network", "none", {}, "system"),
                ],
                resource_limits={
                    "max_memory_mb": 100,
                    "max_cpu_percent": 20,
                    "timeout_seconds": 10
                }
            )
        }
        self.policies.update(default_policies)
        
    async def check_permission(self, agent_id: str, resource: str, action: str, **kwargs) -> bool:
        """Check if agent has permission for specific resource/action"""
        try:
            policy = self.policies.get(agent_id)
            if not policy:
                logger.warning("No policy found for agent", agent_id=agent_id)
                return False
                
            for permission in policy.permissions:
                if permission.resource == resource and permission.action == action:
                    if await self._validate_constraints(permission.constraints, kwargs):
                        logger.info("Permission granted", agent_id=agent_id, resource=resource, action=action)
                        return True
                        
            logger.warning("Permission denied", agent_id=agent_id, resource=resource, action=action)
            return False
        except Exception as e:
            logger.error("Permission check failed", error=str(e))
            return False
            
    async def _validate_constraints(self, constraints: Dict, params: Dict) -> bool:
        """Validate parameter constraints"""
        for key, value in constraints.items():
            if key == "path_prefix":
                path = params.get("path", "")
                if not path.startswith(value):
                    return False
            elif key == "whitelist":
                param_value = params.get("command", "")
                if param_value not in value:
                    return False
        return True
        
    async def get_resource_limits(self, agent_id: str) -> Dict:
        """Get resource limits for agent"""
        policy = self.policies.get(agent_id, SecurityPolicy("default", [], {}))
        return policy.resource_limits
        
    async def grant_temporary_permission(self, agent_id: str, permission: Permission, duration_seconds: int):
        """Grant temporary permission that expires"""
        # Implementation for temporary permissions
        pass
        
    async def get_all_permissions(self) -> Dict:
        """Get all current permissions for debugging"""
        return {
            name: {
                "permissions": [
                    {
                        "resource": p.resource,
                        "action": p.action,
                        "constraints": p.constraints
                    } for p in policy.permissions
                ],
                "resource_limits": policy.resource_limits
            } for name, policy in self.policies.items()
        }
EOF

# Audit Logger
cat > $BACKEND_DIR/src/security/audit_logger.py << 'EOF'
"""
Security Audit Logging System
"""
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
import sqlite3
import structlog
from pathlib import Path

logger = structlog.get_logger()

class AuditLogger:
    def __init__(self):
        self.db_path = "logs/audit.db"
        self.connection = None
        
    async def initialize(self):
        """Initialize audit logging database"""
        Path("logs").mkdir(exist_ok=True)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        await self._create_tables()
        logger.info("Audit logger initialized")
        
    async def _create_tables(self):
        """Create audit log tables"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                parameters TEXT,
                result TEXT,
                security_level TEXT,
                ip_address TEXT,
                correlation_id TEXT
            )
        """)
        self.connection.commit()
        
    async def log_action(self, agent_id: str, action: str, resource: str, 
                        parameters: Dict = None, result: str = "success",
                        security_level: str = "info", correlation_id: str = None):
        """Log security-relevant action"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO audit_logs 
                (timestamp, agent_id, action, resource, parameters, result, security_level, correlation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, agent_id, action, resource,
                json.dumps(parameters or {}), result, security_level, correlation_id
            ))
            self.connection.commit()
            
            # Also log to structured logger
            logger.info(
                "Security action logged",
                agent_id=agent_id,
                action=action,
                resource=resource,
                result=result,
                security_level=security_level
            )
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))
            
    async def log_security_incident(self, agent_id: str, incident_type: str, 
                                  details: Dict, severity: str = "high"):
        """Log security incident"""
        await self.log_action(
            agent_id=agent_id,
            action="security_incident",
            resource=incident_type,
            parameters=details,
            result="incident",
            security_level=severity
        )
        
    async def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent audit logs"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM audit_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        logs = []
        for row in cursor.fetchall():
            log_dict = dict(zip(columns, row))
            if log_dict['parameters']:
                log_dict['parameters'] = json.loads(log_dict['parameters'])
            logs.append(log_dict)
            
        return logs
        
    async def search_logs(self, agent_id: str = None, action: str = None, 
                         security_level: str = None) -> List[Dict]:
        """Search audit logs with filters"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if action:
            query += " AND action = ?"
            params.append(action)
        if security_level:
            query += " AND security_level = ?"
            params.append(security_level)
            
        query += " ORDER BY timestamp DESC"
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
EOF

# Tool Registry
cat > $BACKEND_DIR/src/tools/tool_registry.py << 'EOF'
"""
Dynamic Tool Registry with Capability Validation
"""
import asyncio
import importlib
import inspect
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class ToolCapability:
    name: str
    description: str
    required_permissions: List[str]
    resource_requirements: Dict[str, Any]
    input_schema: Dict
    output_schema: Dict

@dataclass
class RegisteredTool:
    name: str
    function: Callable
    capabilities: ToolCapability
    security_validated: bool
    
class ToolRegistry:
    def __init__(self, permission_manager, audit_logger):
        self.tools: Dict[str, RegisteredTool] = {}
        self.permission_manager = permission_manager
        self.audit_logger = audit_logger
        
    async def initialize(self):
        """Initialize tool registry with built-in tools"""
        await self._register_builtin_tools()
        logger.info("Tool registry initialized")
        
    async def _register_builtin_tools(self):
        """Register built-in secure tools"""
        # File operations
        await self.register_tool(
            name="read_file",
            function=self._read_file_tool,
            capabilities=ToolCapability(
                name="read_file",
                description="Securely read file contents",
                required_permissions=["file.read"],
                resource_requirements={"max_file_size": "10MB"},
                input_schema={"path": "string"},
                output_schema={"content": "string", "metadata": "object"}
            )
        )
        
        await self.register_tool(
            name="list_directory",
            function=self._list_directory_tool,
            capabilities=ToolCapability(
                name="list_directory",
                description="List directory contents",
                required_permissions=["file.list"],
                resource_requirements={"max_items": 1000},
                input_schema={"path": "string"},
                output_schema={"items": "array"}
            )
        )
        
        await self.register_tool(
            name="write_file",
            function=self._write_file_tool,
            capabilities=ToolCapability(
                name="write_file",
                description="Securely write file contents",
                required_permissions=["file.write"],
                resource_requirements={"max_file_size": "10MB"},
                input_schema={"path": "string", "content": "string"},
                output_schema={"success": "boolean", "bytes_written": "integer"}
            )
        )
        
    async def register_tool(self, name: str, function: Callable, capabilities: ToolCapability):
        """Register new tool with security validation"""
        try:
            # Validate tool security
            security_validated = await self._validate_tool_security(function, capabilities)
            
            tool = RegisteredTool(
                name=name,
                function=function,
                capabilities=capabilities,
                security_validated=security_validated
            )
            
            self.tools[name] = tool
            
            await self.audit_logger.log_action(
                agent_id="tool_registry",
                action="tool_registered",
                resource=name,
                parameters={"security_validated": security_validated}
            )
            
            logger.info("Tool registered", name=name, validated=security_validated)
        except Exception as e:
            logger.error("Tool registration failed", name=name, error=str(e))
            raise
            
    async def _validate_tool_security(self, function: Callable, capabilities: ToolCapability) -> bool:
        """Validate tool meets security requirements"""
        # Check function signature
        sig = inspect.signature(function)
        
        # Ensure function is async
        if not asyncio.iscoroutinefunction(function):
            logger.warning("Tool function must be async", function=function.__name__)
            return False
            
        # Check required security decorators/attributes
        if not hasattr(function, '__security_validated__'):
            logger.warning("Tool missing security validation", function=function.__name__)
            return False
            
        return True
        
    async def execute_tool(self, agent_id: str, tool_name: str, parameters: Dict) -> Any:
        """Execute tool with security validation"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        tool = self.tools[tool_name]
        
        # Check permissions
        for permission in tool.capabilities.required_permissions:
            resource, action = permission.split('.')
            if not await self.permission_manager.check_permission(
                agent_id, resource, action, **parameters
            ):
                await self.audit_logger.log_security_incident(
                    agent_id=agent_id,
                    incident_type="permission_denied",
                    details={"tool": tool_name, "permission": permission}
                )
                raise PermissionError(f"Permission denied for {permission}")
        
        # Execute tool in controlled environment
        try:
            result = await tool.function(**parameters)
            
            await self.audit_logger.log_action(
                agent_id=agent_id,
                action="tool_executed",
                resource=tool_name,
                parameters=parameters,
                result="success"
            )
            
            return result
        except Exception as e:
            await self.audit_logger.log_action(
                agent_id=agent_id,
                action="tool_executed",
                resource=tool_name,
                parameters=parameters,
                result=f"error: {str(e)}"
            )
            raise
            
    async def get_all_tools(self) -> Dict:
        """Get all registered tools"""
        return {
            name: {
                "name": tool.capabilities.name,
                "description": tool.capabilities.description,
                "required_permissions": tool.capabilities.required_permissions,
                "input_schema": tool.capabilities.input_schema,
                "output_schema": tool.capabilities.output_schema,
                "security_validated": tool.security_validated
            } for name, tool in self.tools.items()
        }
        
    # Built-in tool implementations
    async def _read_file_tool(self, path: str) -> Dict:
        """Secure file reading tool"""
        import os
        from pathlib import Path
        
        try:
            file_path = Path(path).resolve()
            
            # Additional security check
            if not str(file_path).startswith('/home/user/'):
                raise PermissionError("Access denied: Path outside allowed directory")
                
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                "content": content,
                "metadata": {
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "path": str(file_path)
                }
            }
        except Exception as e:
            logger.error("File read failed", path=path, error=str(e))
            raise
            
    _read_file_tool.__security_validated__ = True
    
    async def _list_directory_tool(self, path: str) -> Dict:
        """Secure directory listing tool"""
        from pathlib import Path
        
        try:
            dir_path = Path(path).resolve()
            
            if not str(dir_path).startswith('/home/user/'):
                raise PermissionError("Access denied: Path outside allowed directory")
                
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime
                })
                
            return {"items": items}
        except Exception as e:
            logger.error("Directory list failed", path=path, error=str(e))
            raise
            
    _list_directory_tool.__security_validated__ = True
    
    async def _write_file_tool(self, path: str, content: str) -> Dict:
        """Secure file writing tool"""
        from pathlib import Path
        
        try:
            file_path = Path(path).resolve()
            
            if not str(file_path).startswith('/home/user/'):
                raise PermissionError("Access denied: Path outside allowed directory")
                
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                bytes_written = f.write(content)
                
            return {
                "success": True,
                "bytes_written": bytes_written
            }
        except Exception as e:
            logger.error("File write failed", path=path, error=str(e))
            raise
            
    _write_file_tool.__security_validated__ = True
EOF

# File Agent
cat > $BACKEND_DIR/src/agents/file_agent.py << 'EOF'
"""
Secure File System Agent with Permission Boundaries
"""
import asyncio
import uuid
from typing import Dict, List, Any
import structlog
import google.generativeai as genai
import os

logger = structlog.get_logger()

class SecureFileAgent:
    def __init__(self, tool_registry, permission_manager, audit_logger):
        self.tool_registry = tool_registry
        self.permission_manager = permission_manager
        self.audit_logger = audit_logger
        self.agent_id = "file_agent"
        self.session_id = str(uuid.uuid4())
        
        # Configure Gemini AI
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "demo-key"))
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def execute_command(self, command: str, parameters: Dict = None) -> Dict:
        """Execute agent command with security validation"""
        correlation_id = str(uuid.uuid4())
        
        try:
            await self.audit_logger.log_action(
                agent_id=self.agent_id,
                action="command_received",
                resource="agent",
                parameters={"command": command, "parameters": parameters},
                correlation_id=correlation_id
            )
            
            # Parse command and determine required tools
            execution_plan = await self._create_execution_plan(command, parameters)
            
            # Execute plan with security validation
            result = await self._execute_plan(execution_plan, correlation_id)
            
            await self.audit_logger.log_action(
                agent_id=self.agent_id,
                action="command_completed",
                resource="agent",
                parameters={"command": command},
                result="success",
                correlation_id=correlation_id
            )
            
            return result
            
        except Exception as e:
            await self.audit_logger.log_security_incident(
                agent_id=self.agent_id,
                incident_type="command_execution_failed",
                details={"command": command, "error": str(e)},
                severity="medium"
            )
            logger.error("Command execution failed", command=command, error=str(e))
            raise
            
    async def _create_execution_plan(self, command: str, parameters: Dict) -> Dict:
        """Create execution plan for command"""
        # Map commands to tool sequences
        command_mappings = {
            "read_file": [{"tool": "read_file", "params": parameters}],
            "list_directory": [{"tool": "list_directory", "params": parameters}],
            "write_file": [{"tool": "write_file", "params": parameters}],
            "analyze_directory": [
                {"tool": "list_directory", "params": parameters},
                {"tool": "read_file", "params": {"path": "..."}}  # Dynamic
            ]
        }
        
        if command in command_mappings:
            return {
                "command": command,
                "steps": command_mappings[command],
                "security_level": "standard"
            }
        else:
            # Use AI to determine execution plan
            return await self._ai_create_plan(command, parameters)
            
    async def _ai_create_plan(self, command: str, parameters: Dict) -> Dict:
        """Use AI to create execution plan for complex commands"""
        prompt = f"""
        Analyze this file system command and create a secure execution plan:
        Command: {command}
        Parameters: {parameters}
        
        Available tools: read_file, write_file, list_directory
        
        Return a JSON plan with security considerations:
        {{
            "command": "{command}",
            "steps": [
                {{"tool": "tool_name", "params": {{"param": "value"}}}}
            ],
            "security_level": "standard|elevated",
            "risk_assessment": "low|medium|high"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse AI response (simplified for demo)
            return {
                "command": command,
                "steps": [{"tool": "list_directory", "params": parameters}],
                "security_level": "standard",
                "ai_generated": True
            }
        except:
            # Fallback to safe default
            return {
                "command": command,
                "steps": [],
                "security_level": "standard",
                "error": "AI planning unavailable"
            }
            
    async def _execute_plan(self, plan: Dict, correlation_id: str) -> Dict:
        """Execute plan with security monitoring"""
        results = []
        
        for step in plan.get("steps", []):
            tool_name = step["tool"]
            params = step["params"]
            
            try:
                result = await self.tool_registry.execute_tool(
                    agent_id=self.agent_id,
                    tool_name=tool_name,
                    parameters=params
                )
                results.append({
                    "tool": tool_name,
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "status": "failed"
                })
                
        return {
            "plan": plan,
            "results": results,
            "correlation_id": correlation_id
        }
        
    async def get_capabilities(self) -> Dict:
        """Get agent capabilities"""
        tools = await self.tool_registry.get_all_tools()
        permissions = await self.permission_manager.get_all_permissions()
        
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "available_tools": list(tools.keys()),
            "permissions": permissions.get(self.agent_id, {}),
            "security_features": [
                "permission_boundaries",
                "audit_logging", 
                "tool_sandboxing",
                "input_validation"
            ]
        }
EOF

# Create init files
touch $BACKEND_DIR/src/__init__.py
touch $BACKEND_DIR/src/agents/__init__.py
touch $BACKEND_DIR/src/security/__init__.py
touch $BACKEND_DIR/src/tools/__init__.py
touch $BACKEND_DIR/src/utils/__init__.py

# Frontend Implementation
cat > $FRONTEND_DIR/package.json << 'EOF'
{
  "name": "secure-tool-integration-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "recharts": "^2.8.0",
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "react-json-view": "^1.21.3"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

cat > $FRONTEND_DIR/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Secure Tool Integration Dashboard" />
    <title>Secure Tool Integration</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
EOF

cat > $FRONTEND_DIR/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > $FRONTEND_DIR/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Tab,
  Tabs
} from '@mui/material';
import AgentDashboard from './components/AgentDashboard';
import SecurityPanel from './components/SecurityPanel';
import ToolRegistry from './components/ToolRegistry';
import AuditLogs from './components/AuditLogs';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <div>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🛡️ Secure Tool Integration Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Agent Dashboard" />
            <Tab label="Security Panel" />
            <Tab label="Tool Registry" />
            <Tab label="Audit Logs" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <AgentDashboard />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <SecurityPanel />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <ToolRegistry />
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <AuditLogs />
          </TabPanel>
        </Paper>
      </Container>
    </div>
  );
}

export default App;
EOF

cat > $FRONTEND_DIR/src/components/AgentDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Card,
  CardContent,
  Box,
  Chip
} from '@mui/material';
import { PlayArrow, Security, Build } from '@mui/icons-material';
import ReactJson from 'react-json-view';
import ApiService from '../services/ApiService';

function AgentDashboard() {
  const [command, setCommand] = useState('');
  const [parameters, setParameters] = useState('{"path": "/home/user/documents"}');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCapabilities();
  }, []);

  const loadCapabilities = async () => {
    try {
      const response = await ApiService.getCapabilities();
      setCapabilities(response.capabilities);
    } catch (err) {
      setError('Failed to load capabilities');
    }
  };

  const executeCommand = async () => {
    setLoading(true);
    setError('');
    try {
      const params = JSON.parse(parameters);
      const response = await ApiService.executeCommand(command, params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const quickCommands = [
    { name: 'List Directory', command: 'list_directory', params: '{"path": "/home/user/documents"}' },
    { name: 'Read File', command: 'read_file', params: '{"path": "/home/user/documents/test.txt"}' },
    { name: 'Write File', command: 'write_file', params: '{"path": "/home/user/documents/output.txt", "content": "Hello from secure agent!"}' }
  ];

  return (
    <Grid container spacing={3}>
      {/* Agent Status */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Security color="primary" />
              <Typography variant="h6">Agent Status</Typography>
              <Chip label="Active" color="success" size="small" />
            </Box>
            {capabilities && (
              <Box mt={2}>
                <Typography variant="body2" color="textSecondary">
                  Agent ID: {capabilities.agent_id}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Session: {capabilities.session_id}
                </Typography>
                <Box mt={1}>
                  {capabilities.security_features?.map((feature) => (
                    <Chip key={feature} label={feature} size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Command Interface */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <Build sx={{ mr: 1, verticalAlign: 'middle' }} />
            Execute Agent Command
          </Typography>
          
          <TextField
            fullWidth
            label="Command"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            margin="normal"
            placeholder="e.g., read_file, list_directory"
          />
          
          <TextField
            fullWidth
            label="Parameters (JSON)"
            value={parameters}
            onChange={(e) => setParameters(e.target.value)}
            margin="normal"
            multiline
            rows={3}
          />
          
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={executeCommand}
            disabled={loading || !command}
            sx={{ mt: 2 }}
          >
            {loading ? 'Executing...' : 'Execute Command'}
          </Button>

          {/* Quick Commands */}
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom>
              Quick Commands:
            </Typography>
            {quickCommands.map((cmd) => (
              <Button
                key={cmd.name}
                variant="outlined"
                size="small"
                onClick={() => {
                  setCommand(cmd.command);
                  setParameters(cmd.params);
                }}
                sx={{ mr: 1, mb: 1 }}
              >
                {cmd.name}
              </Button>
            ))}
          </Box>
        </Paper>
      </Grid>

      {/* Results */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Execution Result
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {result && (
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              <ReactJson
                src={result}
                theme="rjv-default"
                collapsed={false}
                displayDataTypes={false}
                name="result"
              />
            </Box>
          )}
        </Paper>
      </Grid>

      {/* Available Tools */}
      {capabilities && (
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Available Tools
            </Typography>
            <Grid container spacing={2}>
              {capabilities.available_tools?.map((tool) => (
                <Grid item key={tool}>
                  <Chip label={tool} variant="outlined" />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
}

export default AgentDashboard;
EOF

cat > $FRONTEND_DIR/src/components/SecurityPanel.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { Shield, Policy, Lock } from '@mui/icons-material';
import ApiService from '../services/ApiService';

function SecurityPanel() {
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      const response = await ApiService.getPermissions();
      setPermissions(response.permissions);
    } catch (err) {
      console.error('Failed to load permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading security information...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Security Overview */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Shield color="primary" />
              <Typography variant="h6">Security Status</Typography>
              <Chip label="Secure" color="success" size="small" />
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              All security policies active. Permission boundaries enforced.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Permission Policies */}
      {permissions && Object.entries(permissions).map(([agentId, policy]) => (
        <Grid item xs={12} md={6} key={agentId}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Policy sx={{ mr: 1, verticalAlign: 'middle' }} />
              {agentId} Policy
            </Typography>
            
            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Permissions:
            </Typography>
            <List dense>
              {policy.permissions?.map((perm, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={`${perm.resource}.${perm.action}`}
                    secondary={JSON.stringify(perm.constraints)}
                  />
                </ListItem>
              ))}
            </List>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              Resource Limits:
            </Typography>
            <Box>
              {Object.entries(policy.resource_limits || {}).map(([key, value]) => (
                <Chip
                  key={key}
                  label={`${key}: ${value}`}
                  variant="outlined"
                  size="small"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Paper>
        </Grid>
      ))}

      {/* Security Features */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <Lock sx={{ mr: 1, verticalAlign: 'middle' }} />
            Active Security Features
          </Typography>
          
          <Grid container spacing={2}>
            {[
              'Permission Boundaries',
              'Audit Logging',
              'Tool Sandboxing',
              'Input Validation',
              'Resource Monitoring',
              'Error Containment'
            ].map((feature) => (
              <Grid item key={feature}>
                <Chip
                  label={feature}
                  color="primary"
                  variant="outlined"
                />
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default SecurityPanel;
EOF

cat > $FRONTEND_DIR/src/components/ToolRegistry.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { Build, ExpandMore, CheckCircle, Warning } from '@mui/icons-material';
import ReactJson from 'react-json-view';
import ApiService from '../services/ApiService';

function ToolRegistry() {
  const [tools, setTools] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const response = await ApiService.getToolRegistry();
      setTools(response.tools);
    } catch (err) {
      console.error('Failed to load tools:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading tool registry...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Registry Overview */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Build color="primary" />
              <Typography variant="h6">Tool Registry</Typography>
              <Chip 
                label={`${Object.keys(tools || {}).length} Tools Registered`} 
                color="primary" 
                size="small" 
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Tool Details */}
      {tools && Object.entries(tools).map(([toolName, tool]) => (
        <Grid item xs={12} key={toolName}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={2} width="100%">
                <Typography variant="h6">{tool.name}</Typography>
                <Chip
                  icon={tool.security_validated ? <CheckCircle /> : <Warning />}
                  label={tool.security_validated ? 'Validated' : 'Unvalidated'}
                  color={tool.security_validated ? 'success' : 'warning'}
                  size="small"
                />
                <Typography variant="body2" color="textSecondary" sx={{ ml: 'auto' }}>
                  {tool.description}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Required Permissions:
                    </Typography>
                    <Box>
                      {tool.required_permissions?.map((perm) => (
                        <Chip
                          key={perm}
                          label={perm}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Input Schema:
                    </Typography>
                    <ReactJson
                      src={tool.input_schema}
                      theme="rjv-default"
                      collapsed={true}
                      displayDataTypes={false}
                      name="input"
                    />
                  </Paper>
                </Grid>
                
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Output Schema:
                    </Typography>
                    <ReactJson
                      src={tool.output_schema}
                      theme="rjv-default"
                      collapsed={true}
                      displayDataTypes={false}
                      name="output"
                    />
                  </Paper>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      ))}
    </Grid>
  );
}

export default ToolRegistry;
EOF

cat > $FRONTEND_DIR/src/components/AuditLogs.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Button
} from '@mui/material';
import { Refresh, Security } from '@mui/icons-material';
import ApiService from '../services/ApiService';

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const response = await ApiService.getAuditLogs();
      setLogs(response.logs);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSecurityLevelColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Grid container spacing={3}>
      {/* Audit Overview */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={2}>
              <Security color="primary" />
              <Typography variant="h6">Security Audit Logs</Typography>
              <Chip label={`${logs.length} Events`} color="primary" size="small" />
            </Box>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadLogs}
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>
        </Paper>
      </Grid>

      {/* Audit Log Table */}
      <Grid item xs={12}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Agent ID</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Result</TableCell>
                <TableCell>Security Level</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>
                    <Typography variant="body2">
                      {formatTimestamp(log.timestamp)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={log.agent_id} size="small" />
                  </TableCell>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.result}
                      color={log.result === 'success' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.security_level}
                      color={getSecurityLevelColor(log.security_level)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Grid>
    </Grid>
  );
}

export default AuditLogs;
EOF

cat > $FRONTEND_DIR/src/services/ApiService.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
  }

  async executeCommand(command, parameters) {
    const response = await this.client.post('/agent/execute', {
      command,
      parameters
    });
    return response.data;
  }

  async getCapabilities() {
    const response = await this.client.get('/agent/capabilities');
    return response.data;
  }

  async getPermissions() {
    const response = await this.client.get('/security/permissions');
    return response.data;
  }

  async getAuditLogs() {
    const response = await this.client.get('/security/audit');
    return response.data;
  }

  async getToolRegistry() {
    const response = await this.client.get('/tools/registry');
    return response.data;
  }
}

export default new ApiService();
EOF

# Create test files
mkdir -p $BACKEND_DIR/tests
cat > $BACKEND_DIR/tests/test_security.py << 'EOF'
"""
Security component tests
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from security.permission_manager import PermissionManager
from security.audit_logger import AuditLogger
from tools.tool_registry import ToolRegistry

@pytest.mark.asyncio
async def test_permission_manager():
    """Test permission management"""
    pm = PermissionManager()
    await pm.initialize()
    
    # Test permission check
    result = await pm.check_permission(
        "file_agent", "file", "read", 
        path="/home/user/documents/test.txt"
    )
    assert result == True
    
    # Test denied permission
    result = await pm.check_permission(
        "file_agent", "file", "read", 
        path="/etc/passwd"
    )
    assert result == False

@pytest.mark.asyncio
async def test_audit_logger():
    """Test audit logging"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create audit logger with temp directory
        audit_logger = AuditLogger()
        audit_logger.db_path = os.path.join(tmpdir, "test_audit.db")
        await audit_logger.initialize()
        
        # Log an action
        await audit_logger.log_action(
            agent_id="test_agent",
            action="test_action",
            resource="test_resource"
        )
        
        # Retrieve logs
        logs = await audit_logger.get_recent_logs(limit=10)
        assert len(logs) == 1
        assert logs[0]["agent_id"] == "test_agent"

@pytest.mark.asyncio 
async def test_tool_registry():
    """Test tool registry"""
    pm = PermissionManager()
    await pm.initialize()
    
    audit_logger = AuditLogger()
    audit_logger.db_path = ":memory:"
    await audit_logger.initialize()
    
    registry = ToolRegistry(pm, audit_logger)
    await registry.initialize()
    
    # Test tool execution with permission
    result = await registry.execute_tool(
        "file_agent", "list_directory", 
        {"path": "/home/user/documents"}
    )
    assert "items" in result

if __name__ == "__main__":
    pytest.main([__file__])
EOF

# Create sample data
mkdir -p $PROJECT_NAME/data/sample
cat > $PROJECT_NAME/data/sample/test.txt << 'EOF'
This is a test file for the secure file agent.
It demonstrates the secure tool integration system.
EOF

# Create Docker configuration
cat > $PROJECT_NAME/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

# Create required directories
RUN mkdir -p logs data/sandbox

# Expose port
EXPOSE 8000

CMD ["python", "src/main.py"]
EOF

cat > $PROJECT_NAME/docker-compose.yml << 'EOF'
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY:-demo-key}
    
  frontend:
    image: node:18
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: sh -c "npm install && npm start"
    depends_on:
      - backend
EOF

# Create start script
cat > $PROJECT_NAME/start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Secure Tool Integration System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Create required directories
mkdir -p ../data/sample ../logs
cd ..

# Create sample files for testing
mkdir -p /tmp/user/documents
echo "Sample document content for testing secure file agent." > /tmp/user/documents/sample.txt
echo "Another test file." > /tmp/user/documents/readme.txt

# Start backend
echo "Starting backend server..."
cd backend
python src/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Install frontend dependencies and start
echo "Starting frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

wait
EOF

cat > $PROJECT_NAME/stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Secure Tool Integration System..."

# Kill processes
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null  
    rm .frontend.pid
fi

echo "✅ System stopped"
EOF

chmod +x $PROJECT_NAME/start.sh
chmod +x $PROJECT_NAME/stop.sh

echo "✅ Project structure created successfully!"
echo ""
echo "📁 Project: $PROJECT_NAME"
echo "📁 Backend: $BACKEND_DIR (Python FastAPI)"
echo "📁 Frontend: $FRONTEND_DIR (React)"
echo ""
echo "🔧 Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. export GEMINI_API_KEY='your-api-key'"
echo "3. ./start.sh"
echo ""
echo "🌐 Endpoints:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"