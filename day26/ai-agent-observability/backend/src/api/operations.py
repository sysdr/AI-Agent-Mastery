from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from services.operations_service import OperationsService

router = APIRouter()
operations_service = OperationsService()

@router.get("/")
async def get_operations(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000)
) -> List[Dict]:
    """Get operations with optional filtering"""
    return await operations_service.get_operations(status, limit)

@router.get("/{operation_id}")
async def get_operation_details(operation_id: str) -> Dict:
    """Get detailed operation information"""
    operation = await operations_service.get_operation_details(operation_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return operation

@router.post("/start")
async def start_operation(
    operation_type: str,
    description: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """Start a new operation"""
    operation_id = await operations_service.start_operation(
        operation_type, description, metadata
    )
    return {"operation_id": operation_id, "status": "started"}

@router.post("/{operation_id}/update")
async def update_operation(
    operation_id: str,
    status: Optional[str] = None,
    metrics: Optional[Dict] = None
) -> Dict:
    """Update an operation"""
    await operations_service.update_operation(operation_id, status, metrics)
    return {"status": "updated"}
