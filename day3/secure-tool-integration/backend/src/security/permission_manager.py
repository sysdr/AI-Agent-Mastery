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
                    Permission("file", "read", {"path_prefix": "/tmp/user/documents"}, "system"),
                    Permission("file", "write", {"path_prefix": "/tmp/user/documents"}, "system"),
                    Permission("file", "list", {"path_prefix": "/tmp/user"}, "system"),
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
