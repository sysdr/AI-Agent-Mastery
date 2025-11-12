from sqlalchemy import select
from app.models.integration import Event
from app.utils.database import AsyncSessionLocal
import uuid
from datetime import datetime
import json
import hashlib

class EventStore:
    def __init__(self):
        self.session = None
    
    async def initialize(self):
        """Initialize event store"""
        pass
    
    async def append_event(
        self,
        event_type: str,
        aggregate_id: str,
        aggregate_type: str,
        event_data: dict,
        user_id: str = None,
        correlation_id: str = None
    ) -> Event:
        """Append an event to the event store"""
        async with AsyncSessionLocal() as session:
            # Get next sequence number
            result = await session.execute(
                select(Event.sequence_number)
                .where(Event.aggregate_id == aggregate_id)
                .order_by(Event.sequence_number.desc())
                .limit(1)
            )
            last_seq = result.scalar_one_or_none()
            next_seq = (last_seq or 0) + 1
            
            # Create event
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                event_data=event_data,
                event_metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0"
                },
                user_id=user_id,
                correlation_id=correlation_id,
                sequence_number=next_seq,
                timestamp=datetime.utcnow(),
                signature=self._sign_event(event_data)
            )
            
            session.add(event)
            await session.commit()
            await session.refresh(event)
            
            return event
    
    async def get_events(
        self,
        aggregate_id: str = None,
        event_type: str = None,
        limit: int = 100
    ) -> list[Event]:
        """Retrieve events from the store"""
        async with AsyncSessionLocal() as session:
            query = select(Event).where(Event.is_deleted == False)
            
            if aggregate_id:
                query = query.where(Event.aggregate_id == aggregate_id)
            if event_type:
                query = query.where(Event.event_type == event_type)
            
            query = query.order_by(Event.timestamp.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    def _sign_event(self, event_data: dict) -> str:
        """Create digital signature for event"""
        data_str = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def close(self):
        """Cleanup resources"""
        pass

event_store = EventStore()
