from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import structlog

logger = structlog.get_logger()

class OperationsService:
    def __init__(self):
        self.operations: List[Dict] = []
        self.active_operations: Dict[str, Dict] = {}
        
    async def start_operation(self, operation_type: str, 
                              description: str, metadata: Dict = None) -> str:
        """Start a new operation"""
        operation_id = f"op_{int(datetime.now().timestamp() * 1000000)}"
        
        operation = {
            "operation_id": operation_id,
            "type": operation_type,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "metadata": metadata or {},
            "metrics": {}
        }
        
        self.active_operations[operation_id] = operation
        
        logger.info("Started operation", operation_id=operation_id, type=operation_type)
        return operation_id
    
    async def update_operation(self, operation_id: str, 
                               status: Optional[str] = None,
                               metrics: Optional[Dict] = None):
        """Update an operation"""
        if operation_id not in self.active_operations:
            logger.warning("Operation not found", operation_id=operation_id)
            return
        
        operation = self.active_operations[operation_id]
        
        if status:
            operation["status"] = status
        
        if metrics:
            operation["metrics"].update(metrics)
        
        if status and status in ["completed", "failed", "cancelled"]:
            operation["end_time"] = datetime.now().isoformat()
            self.operations.append(operation)
            del self.active_operations[operation_id]
            
            # Keep only last 1000 completed operations
            if len(self.operations) > 1000:
                self.operations = self.operations[-1000:]
    
    async def get_operations(self, status: Optional[str] = None, 
                            limit: int = 50) -> List[Dict]:
        """Get operations with optional filtering"""
        all_ops = list(self.active_operations.values()) + self.operations
        
        if status:
            all_ops = [op for op in all_ops if op.get("status") == status]
        
        return sorted(all_ops, 
                     key=lambda x: x.get("start_time", ""), 
                     reverse=True)[:limit]
    
    async def get_operation_details(self, operation_id: str) -> Optional[Dict]:
        """Get detailed operation information"""
        if operation_id in self.active_operations:
            return self.active_operations[operation_id]
        
        for op in self.operations:
            if op["operation_id"] == operation_id:
                return op
        
        return None
    
    async def health_check(self) -> Dict:
        """Service health check"""
        return {
            "status": "healthy",
            "active_operations": len(self.active_operations),
            "total_operations": len(self.operations)
        }
