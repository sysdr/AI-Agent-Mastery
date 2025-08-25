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
