"""
Workflow Engine - Manages workflow state and coordination
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import json

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    task_id: str
    name: str
    agent_type: str
    dependencies: List[str]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: TaskStatus
    created_at: float
    updated_at: float
    execution_time: float = 0.0

class WorkflowEngine:
    """Orchestrates task execution with dependency management"""
    
    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        
    async def create_task(
        self, 
        task_id: str,
        name: str,
        agent_type: str,
        dependencies: List[str] = None,
        inputs: Dict[str, Any] = None
    ) -> Task:
        """Create a new task with dependencies"""
        
        task = Task(
            task_id=task_id,
            name=name,
            agent_type=agent_type,
            dependencies=dependencies or [],
            inputs=inputs or {},
            outputs={},
            status=TaskStatus.PENDING,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        self.active_tasks[task_id] = task
        logger.info(f"Created task {task_id}: {name}")
        
        return task
    
    async def can_execute_task(self, task_id: str) -> bool:
        """Check if task dependencies are satisfied"""
        
        if task_id not in self.active_tasks:
            return False
            
        task = self.active_tasks[task_id]
        
        # Check all dependencies are completed
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
                
        return True
    
    async def execute_ready_tasks(self) -> List[str]:
        """Execute all tasks that are ready to run"""
        
        ready_tasks = []
        
        for task_id, task in self.active_tasks.items():
            if task.status == TaskStatus.PENDING and await self.can_execute_task(task_id):
                ready_tasks.append(task_id)
                
        return ready_tasks
    
    async def start_task_execution(self, task_id: str):
        """Mark task as running"""
        
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.RUNNING
            task.updated_at = time.time()
            
            logger.info(f"Started task execution: {task_id}")
    
    async def complete_task(self, task_id: str, outputs: Dict[str, Any]):
        """Mark task as completed with outputs"""
        
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.outputs = outputs
            task.updated_at = time.time()
            task.execution_time = task.updated_at - task.created_at
            
            # Move to completed tasks
            self.completed_tasks[task_id] = task
            del self.active_tasks[task_id]
            
            logger.info(f"Completed task: {task_id}")
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error details"""
        
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.FAILED
            task.outputs = {"error": error}
            task.updated_at = time.time()
            
            # Move to failed tasks
            self.failed_tasks[task_id] = task
            del self.active_tasks[task_id]
            
            logger.error(f"Failed task {task_id}: {error}")
    
    async def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Calculate workflow progress and status"""
        
        total_tasks = len(self.active_tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        
        if total_tasks == 0:
            progress = 0.0
        else:
            progress = (completed / total_tasks) * 100.0
            
        return {
            "progress": progress,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "active_tasks": len(self.active_tasks)
        }
