from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.utils.database import get_db
from app.models.integration import IntegrationRequest, RequestStatus
from app.api.schemas.integration_schemas import (
    IntegrationRequestSchema,
    IntegrationResponseSchema,
    CustomerQueryRequest,
    CustomerUpdateRequest
)
from app.services.integration.event_sourcing import event_store
from app.services.integration.cache_service import cache_service
from app.services.transformation.data_transformer import data_transformer
from app.services.legacy.legacy_connector import legacy_connector
import uuid
import time
from datetime import datetime

router = APIRouter()

@router.post("/request", response_model=IntegrationResponseSchema)
async def create_integration_request(
    request: IntegrationRequestSchema,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Create new integration request"""
    start_time = time.time()
    correlation_id = http_request.state.correlation_id
    
    # Create integration request record
    integration_req = IntegrationRequest(
        correlation_id=correlation_id,
        request_type=request.request_type,
        source_system="modern_api",
        target_system=request.target_system.value,
        request_data=request.data,
        status=RequestStatus.PENDING
    )
    
    db.add(integration_req)
    await db.commit()
    await db.refresh(integration_req)
    
    # Log event
    await event_store.append_event(
        event_type="IntegrationRequestCreated",
        aggregate_id=correlation_id,
        aggregate_type="IntegrationRequest",
        event_data=request.data,
        correlation_id=correlation_id
    )
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return IntegrationResponseSchema(
        correlation_id=correlation_id,
        status="accepted",
        processing_time_ms=processing_time
    )

@router.get("/customer/{customer_id}", response_model=IntegrationResponseSchema)
async def get_customer(
    customer_id: str,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get customer data with caching and transformation"""
    start_time = time.time()
    correlation_id = http_request.state.correlation_id
    
    # Create integration request record for tracking
    integration_req = IntegrationRequest(
        correlation_id=correlation_id,
        request_type="customer_query",
        source_system="modern_api",
        target_system="legacy_system",
        request_data={"customer_id": customer_id},
        status=RequestStatus.PROCESSING
    )
    db.add(integration_req)
    await db.commit()
    
    # Check cache
    cache_key = f"customer:{customer_id}"
    cached_data = await cache_service.get(cache_key)
    
    if cached_data:
        processing_time = int((time.time() - start_time) * 1000)
        integration_req.status = RequestStatus.COMPLETED
        integration_req.processing_time_ms = processing_time
        integration_req.response_data = cached_data
        await db.commit()
        
        return IntegrationResponseSchema(
            correlation_id=correlation_id,
            status="success",
            data=cached_data,
            processing_time_ms=processing_time,
            cached=True
        )
    
    try:
        # Query legacy system
        legacy_data = await legacy_connector.query_customer(customer_id)
        
        # Transform to modern format
        modern_data = data_transformer.to_modern_format(legacy_data)
        
        # Cache the result
        await cache_service.set(cache_key, modern_data, ttl=300)
        
        # Log event
        await event_store.append_event(
            event_type="CustomerQueried",
            aggregate_id=customer_id,
            aggregate_type="Customer",
            event_data={"customer_id": customer_id},
            correlation_id=correlation_id
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        integration_req.status = RequestStatus.COMPLETED
        integration_req.processing_time_ms = processing_time
        integration_req.response_data = modern_data
        await db.commit()
        
        return IntegrationResponseSchema(
            correlation_id=correlation_id,
            status="success",
            data=modern_data,
            processing_time_ms=processing_time,
            cached=False
        )
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        integration_req.status = RequestStatus.FAILED
        integration_req.processing_time_ms = processing_time
        integration_req.error_message = str(e)
        await db.commit()
        
        return IntegrationResponseSchema(
            correlation_id=correlation_id,
            status="error",
            error=str(e),
            processing_time_ms=processing_time
        )

@router.put("/customer/{customer_id}", response_model=IntegrationResponseSchema)
async def update_customer(
    customer_id: str,
    update_data: CustomerUpdateRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Update customer with transformation and event sourcing"""
    start_time = time.time()
    correlation_id = http_request.state.correlation_id
    
    # Create integration request record for tracking
    integration_req = IntegrationRequest(
        correlation_id=correlation_id,
        request_type="customer_update",
        source_system="modern_api",
        target_system="legacy_system",
        request_data={"customer_id": customer_id, "update_data": update_data.dict()},
        status=RequestStatus.PROCESSING
    )
    db.add(integration_req)
    await db.commit()
    
    try:
        # Transform to legacy format
        modern_data = update_data.dict(exclude_unset=True)
        modern_data.pop('customer_id', None)
        legacy_data = data_transformer.to_legacy_format(modern_data)
        
        # Update legacy system
        success = await legacy_connector.update_customer(customer_id, legacy_data)
        
        if success:
            # Invalidate cache
            await cache_service.delete(f"customer:{customer_id}")
            
            # Log event
            await event_store.append_event(
                event_type="CustomerUpdated",
                aggregate_id=customer_id,
                aggregate_type="Customer",
                event_data={
                    "customer_id": customer_id,
                    "changes": modern_data
                },
                correlation_id=correlation_id
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        integration_req.status = RequestStatus.COMPLETED if success else RequestStatus.FAILED
        integration_req.processing_time_ms = processing_time
        integration_req.response_data = {"success": success}
        await db.commit()
        
        return IntegrationResponseSchema(
            correlation_id=correlation_id,
            status="success" if success else "failed",
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        integration_req.status = RequestStatus.FAILED
        integration_req.processing_time_ms = processing_time
        integration_req.error_message = str(e)
        await db.commit()
        
        return IntegrationResponseSchema(
            correlation_id=correlation_id,
            status="error",
            error=str(e),
            processing_time_ms=processing_time
        )

@router.get("/stats")
async def get_integration_stats(db: AsyncSession = Depends(get_db)):
    """Get integration statistics"""
    try:
        total_requests = await db.execute(
            select(func.count(IntegrationRequest.id))
        )
        
        successful_requests = await db.execute(
            select(func.count(IntegrationRequest.id))
            .where(IntegrationRequest.status == RequestStatus.COMPLETED)
        )
        
        failed_requests = await db.execute(
            select(func.count(IntegrationRequest.id))
            .where(IntegrationRequest.status == RequestStatus.FAILED)
        )
        
        avg_processing_time = await db.execute(
            select(func.avg(IntegrationRequest.processing_time_ms))
            .where(IntegrationRequest.status == RequestStatus.COMPLETED)
        )
        
        return {
            "total_requests": total_requests.scalar_one() or 0,
            "successful": successful_requests.scalar_one() or 0,
            "failed": failed_requests.scalar_one() or 0,
            "average_processing_time_ms": round(avg_processing_time.scalar_one() or 0, 2)
        }
    except Exception as e:
        # Return default stats if database query fails
        # This ensures CORS headers are still sent
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )
