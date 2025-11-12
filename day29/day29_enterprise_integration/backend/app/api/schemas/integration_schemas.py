from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SystemType(str, Enum):
    MODERN = "modern"
    LEGACY = "legacy"

class IntegrationRequestSchema(BaseModel):
    request_type: str = Field(..., description="Type of integration request")
    target_system: SystemType
    data: Dict[str, Any]
    priority: Optional[int] = 5
    async_processing: Optional[bool] = False

class IntegrationResponseSchema(BaseModel):
    correlation_id: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    cached: bool = False
    
class CustomerQueryRequest(BaseModel):
    customer_id: str
    include_transactions: bool = False

class CustomerUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Allow both snake_case and camelCase
    
    customer_id: Optional[str] = None  # Optional since it comes from path parameter
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: Optional[str] = None
    active: Optional[bool] = None

class EventSchema(BaseModel):
    event_id: str
    event_type: str
    aggregate_id: str
    timestamp: datetime
    data: Dict[str, Any]
    
class CircuitStateSchema(BaseModel):
    service_name: str
    state: str
    failure_count: int
    last_failure_time: Optional[datetime] = None
