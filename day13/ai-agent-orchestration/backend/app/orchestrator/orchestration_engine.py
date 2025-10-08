import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import structlog
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential

from tools.tool_manager import ToolManager
from security.security_validator import SecurityValidator
from trackers.cost_tracker import CostTracker
from monitoring.metrics_collector import MetricsCollector
from recovery.failure_handler import FailureHandler

logger = structlog.get_logger()

@dataclass
class OrchestrationRequest:
    query: str
    tools_config: Dict[str, Any]
    security_level: str
    request_id: str
    timestamp: float

@dataclass
class OrchestrationResult:
    success: bool
    data: Dict[str, Any]
    cost: float
    execution_time: float
    tools_used: List[str]
    security_score: float
    errors: List[str] = None

class OrchestrationEngine:
    def __init__(self):
        self.tool_manager = ToolManager()
        self.security_validator = SecurityValidator()
        self.cost_tracker = CostTracker()
        self.metrics_collector = MetricsCollector()
        self.failure_handler = FailureHandler()
        self.active_orchestrations = {}
        self.max_parallel = 5
        
    async def initialize(self):
        """Initialize all components"""
        await self.tool_manager.initialize()
        await self.security_validator.initialize()
        await self.cost_tracker.initialize()
        logger.info("Orchestration engine initialized")
        
    async def execute_research(self, query: str, tools_config: Dict, security_level: str) -> Dict:
        """Execute research with orchestrated tools"""
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = time.time()
        
        request = OrchestrationRequest(
            query=query,
            tools_config=tools_config,
            security_level=security_level,
            request_id=request_id,
            timestamp=start_time
        )
        
        self.active_orchestrations[request_id] = request
        
        try:
            # Security validation
            await self.security_validator.validate_request(request)
            
            # Plan tool execution
            execution_plan = await self.plan_tool_execution(request)
            
            # Execute tools in parallel
            results = await self.execute_tools_parallel(execution_plan)
            
            # Validate and synthesize results
            final_result = await self.synthesize_results(results, request)
            
            # Track costs and metrics
            execution_time = time.time() - start_time
            await self.track_execution(request, final_result, execution_time)
            
            return final_result
            
        except Exception as e:
            await self.failure_handler.handle_failure(request_id, str(e))
            raise
        finally:
            self.active_orchestrations.pop(request_id, None)
    
    async def plan_tool_execution(self, request: OrchestrationRequest) -> Dict:
        """Plan which tools to execute and in what order"""
        tools_needed = await self.tool_manager.determine_tools(request.query)
        
        # Create execution plan with dependencies
        execution_plan = {
            "parallel_groups": [],
            "sequential_steps": [],
            "fallback_tools": []
        }
        
        # Group tools that can run in parallel
        primary_tools = ["web_search", "document_analyzer", "fact_checker"]
        synthesis_tools = ["content_synthesizer", "bias_detector"]
        
        execution_plan["parallel_groups"].append(primary_tools)
        execution_plan["sequential_steps"].append(synthesis_tools)
        
        return execution_plan
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def execute_tools_parallel(self, execution_plan: Dict) -> Dict:
        """Execute tools in parallel with resource management"""
        results = {}
        
        # Execute parallel groups
        for group in execution_plan["parallel_groups"]:
            semaphore = asyncio.Semaphore(self.max_parallel)
            tasks = []
            
            for tool_name in group:
                task = self.execute_single_tool(tool_name, semaphore)
                tasks.append(task)
            
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(group_results):
                tool_name = group[i]
                if isinstance(result, Exception):
                    logger.error(f"Tool {tool_name} failed", error=str(result))
                    results[tool_name] = {"error": str(result)}
                else:
                    results[tool_name] = result
        
        return results
    
    async def execute_single_tool(self, tool_name: str, semaphore: asyncio.Semaphore) -> Dict:
        """Execute single tool with resource constraints"""
        async with semaphore:
            start_time = time.time()
            try:
                result = await self.tool_manager.execute_tool(tool_name)
                execution_time = time.time() - start_time
                
                # Track cost
                await self.cost_tracker.track_tool_usage(tool_name, execution_time)
                
                return {
                    "success": True,
                    "data": result,
                    "execution_time": execution_time
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "execution_time": time.time() - start_time
                }
    
    async def synthesize_results(self, results: Dict, request: OrchestrationRequest) -> Dict:
        """Synthesize and validate final results"""
        # Filter successful results
        successful_results = {
            tool: result for tool, result in results.items() 
            if result.get("success", False)
        }
        
        # Security validation of results
        validated_results = await self.security_validator.validate_results(successful_results)
        
        # Synthesize final response
        synthesis = await self.tool_manager.synthesize_response(
            validated_results, request.query
        )
        
        return {
            "query": request.query,
            "synthesis": synthesis,
            "sources": list(successful_results.keys()),
            "security_validated": True,
            "timestamp": time.time()
        }
    
    async def track_execution(self, request: OrchestrationRequest, result: Dict, execution_time: float):
        """Track metrics and costs"""
        total_cost = await self.cost_tracker.get_request_cost(request.request_id)
        
        await self.metrics_collector.record_orchestration(
            request_id=request.request_id,
            execution_time=execution_time,
            total_cost=total_cost,
            tools_used=result.get("sources", []),
            success=True
        )
    
    async def get_active_count(self) -> int:
        """Get number of active orchestrations"""
        return len(self.active_orchestrations)
    
    async def get_circuit_breaker_status(self) -> Dict:
        """Get circuit breaker status for all tools"""
        return await self.tool_manager.get_circuit_breaker_status()
    
    async def cleanup(self):
        """Clean up resources"""
        await self.tool_manager.cleanup()
        await self.cost_tracker.cleanup()
