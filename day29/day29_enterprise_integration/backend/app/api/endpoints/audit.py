from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.database import get_db
from app.models.integration import Event
from app.api.schemas.integration_schemas import EventSchema
from typing import List, Optional

router = APIRouter()

@router.get("/events", response_model=List[EventSchema])
async def get_events(
    aggregate_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get audit events"""
    query = select(Event).where(Event.is_deleted == False)
    
    if aggregate_id:
        query = query.where(Event.aggregate_id == aggregate_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    query = query.order_by(Event.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [
        EventSchema(
            event_id=event.event_id,
            event_type=event.event_type,
            aggregate_id=event.aggregate_id,
            timestamp=event.timestamp,
            data=event.event_data
        )
        for event in events
    ]

@router.get("/events/types")
async def get_event_types(db: AsyncSession = Depends(get_db)):
    """Get list of event types"""
    result = await db.execute(
        select(Event.event_type).distinct()
    )
    return {"event_types": [row[0] for row in result]}
