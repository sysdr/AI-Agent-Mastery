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
            if not (str(file_path).startswith('/home/user/') or str(file_path).startswith('/tmp/user/')):
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
            
            if not (str(dir_path).startswith('/home/user/') or str(dir_path).startswith('/tmp/user/')):
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
            
            if not (str(file_path).startswith('/home/user/') or str(file_path).startswith('/tmp/user/')):
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
