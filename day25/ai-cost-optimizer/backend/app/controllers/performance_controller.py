from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from app.services.performance_monitor import PerformanceMonitorService

router = APIRouter(prefix="/api/performance", tags=["performance"])

class PerformanceController:
    def __init__(self, performance_service: PerformanceMonitorService):
        self.performance_service = performance_service
    
    async def start_monitoring_agent(self, agent_id: str) -> Dict[str, Any]:
        """Start monitoring performance for agent"""
        try:
            # Start monitoring in background
            import asyncio
            asyncio.create_task(self.performance_service.start_monitoring(agent_id))
            
            return {
                'success': True,
                'message': f'Performance monitoring started for agent {agent_id}',
                'agent_id': agent_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_monitoring_agent(self, agent_id: str) -> Dict[str, Any]:
        """Stop monitoring performance for agent"""
        try:
            await self.performance_service.stop_monitoring()
            
            return {
                'success': True,
                'message': f'Performance monitoring stopped for agent {agent_id}',
                'agent_id': agent_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
