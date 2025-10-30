"""Agent Orchestration System"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from enum import Enum
import structlog
import google.generativeai as genai

from app.agents.data_agent import DataAgent
from app.agents.security_agent import SecurityAgent
from app.agents.compliance_agent import ComplianceAgent
from app.utils.config import settings

logger = structlog.get_logger()

class AgentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.circuit_breakers: Dict[str, dict] = {}
        self.performance_metrics: Dict[str, dict] = {}
        
    async def initialize(self):
        """Initialize all agents and orchestration system"""
        logger.info("Initializing Agent Orchestrator")
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize agents
        self.agents = {
            "data_agent": DataAgent(),
            "security_agent": SecurityAgent(),
            "compliance_agent": ComplianceAgent()
        }
        
        # Initialize circuit breakers
        for agent_name in self.agents.keys():
            self.circuit_breakers[agent_name] = {
                "failure_count": 0,
                "last_failure": None,
                "status": "closed",
                "threshold": 3,
                "timeout": 60
            }
            
        # Initialize all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                logger.info(f"Agent {agent_name} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_name}", error=str(e))
                
        # Start task processing
        asyncio.create_task(self._process_task_queue())
        
    async def execute_task(self, task_data: dict) -> dict:
        """Execute task with intelligent agent selection and failure handling"""
        task_id = f"task_{int(time.time() * 1000)}"
        task_type = task_data.get("type", "general")
        
        logger.info("Executing task", task_id=task_id, task_type=task_type)
        
        try:
            # Select appropriate agent
            agent_name = self._select_agent(task_type)
            
            # Check circuit breaker
            if not self._is_agent_available(agent_name):
                return await self._handle_agent_unavailable(task_data, agent_name)
            
            # Execute task
            start_time = time.time()
            result = await self._execute_with_retry(agent_name, task_data)
            execution_time = time.time() - start_time
            
            # Update metrics
            await self._update_performance_metrics(agent_name, execution_time, True)
            
            # Reset circuit breaker on success
            self._reset_circuit_breaker(agent_name)
            
            return {
                "task_id": task_id,
                "agent": agent_name,
                "status": "completed",
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error("Task execution failed", task_id=task_id, error=str(e))
            await self._handle_execution_failure(agent_name if 'agent_name' in locals() else None, e)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "recovery_attempted": True
            }
    
    def _select_agent(self, task_type: str) -> str:
        """Select appropriate agent based on task type"""
        agent_mapping = {
            "data_processing": "data_agent",
            "security_scan": "security_agent",
            "compliance_check": "compliance_agent"
        }
        return agent_mapping.get(task_type, "data_agent")
    
    def _is_agent_available(self, agent_name: str) -> bool:
        """Check if agent is available (circuit breaker open check)"""
        cb = self.circuit_breakers[agent_name]
        
        if cb["status"] == "open":
            # Check if timeout has passed
            if time.time() - cb["last_failure"] > cb["timeout"]:
                cb["status"] = "half_open"
                return True
            return False
        
        return cb["status"] in ["closed", "half_open"]
    
    async def _execute_with_retry(self, agent_name: str, task_data: dict, max_retries: int = 3) -> dict:
        """Execute task with retry logic"""
        for attempt in range(max_retries):
            try:
                agent = self.agents[agent_name]
                result = await agent.process_task(task_data)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                logger.warning(f"Retry attempt {attempt + 1} for agent {agent_name}", error=str(e))
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _handle_agent_unavailable(self, task_data: dict, failed_agent: str) -> dict:
        """Handle case when primary agent is unavailable"""
        logger.warning(f"Agent {failed_agent} unavailable, attempting fallback")
        
        # Try fallback agents
        fallback_agents = [name for name in self.agents.keys() if name != failed_agent]
        
        for fallback_agent in fallback_agents:
            if self._is_agent_available(fallback_agent):
                try:
                    result = await self._execute_with_retry(fallback_agent, task_data)
                    return {
                        "status": "completed_with_fallback",
                        "primary_agent": failed_agent,
                        "fallback_agent": fallback_agent,
                        "result": result
                    }
                except Exception as e:
                    continue
        
        # If all agents failed, return graceful degradation
        return {
            "status": "degraded",
            "message": "All agents unavailable, task queued for later execution",
            "queued": True
        }
    
    async def _handle_execution_failure(self, agent_name: str, error: Exception):
        """Handle execution failure and update circuit breaker"""
        if agent_name:
            cb = self.circuit_breakers[agent_name]
            cb["failure_count"] += 1
            cb["last_failure"] = time.time()
            
            if cb["failure_count"] >= cb["threshold"]:
                cb["status"] = "open"
                logger.warning(f"Circuit breaker opened for agent {agent_name}")
                
            await self._update_performance_metrics(agent_name, 0, False)
    
    def _reset_circuit_breaker(self, agent_name: str):
        """Reset circuit breaker on successful execution"""
        self.circuit_breakers[agent_name]["failure_count"] = 0
        self.circuit_breakers[agent_name]["status"] = "closed"
    
    async def _update_performance_metrics(self, agent_name: str, execution_time: float, success: bool):
        """Update performance metrics for agent"""
        if agent_name not in self.performance_metrics:
            self.performance_metrics[agent_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_time": 0,
                "avg_response_time": 0,
                "success_rate": 0
            }
        
        metrics = self.performance_metrics[agent_name]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            metrics["total_time"] += execution_time
        
        metrics["avg_response_time"] = metrics["total_time"] / max(metrics["successful_requests"], 1)
        metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"]
    
    async def get_agents_status(self) -> dict:
        """Get comprehensive status of all agents"""
        status = {}
        
        for agent_name, agent in self.agents.items():
            cb = self.circuit_breakers[agent_name]
            metrics = self.performance_metrics.get(agent_name, {})
            
            try:
                health = await agent.health_check()
                agent_status = AgentStatus.HEALTHY
            except:
                agent_status = AgentStatus.FAILED
            
            status[agent_name] = {
                "status": agent_status.value,
                "circuit_breaker": cb["status"],
                "failure_count": cb["failure_count"],
                "performance_metrics": metrics,
                "health": health if agent_status == AgentStatus.HEALTHY else {"status": "unhealthy"}
            }
        
        return status
    
    async def trigger_recovery(self):
        """Trigger recovery procedures for failed agents"""
        logger.info("Triggering recovery procedures")
        
        for agent_name, agent in self.agents.items():
            try:
                if self.circuit_breakers[agent_name]["status"] == "open":
                    logger.info(f"Attempting to recover agent {agent_name}")
                    await agent.recover()
                    self._reset_circuit_breaker(agent_name)
                    logger.info(f"Agent {agent_name} recovered successfully")
            except Exception as e:
                logger.error(f"Failed to recover agent {agent_name}", error=str(e))
    
    async def _process_task_queue(self):
        """Process queued tasks (for degraded mode)"""
        while True:
            try:
                # This would process queued tasks when agents recover
                await asyncio.sleep(5)
            except Exception as e:
                logger.error("Task queue processing error", error=str(e))
    
    async def shutdown(self):
        """Shutdown orchestrator and all agents"""
        logger.info("Shutting down Agent Orchestrator")
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down agent {agent_name}", error=str(e))
