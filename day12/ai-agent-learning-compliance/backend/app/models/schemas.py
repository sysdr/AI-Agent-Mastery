from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    VIEW = "view"
    CLICK = "click"
    LIKE = "like"
    DISLIKE = "dislike"
    SHARE = "share"
    PURCHASE = "purchase"

class UserInteraction(BaseModel):
    user_id: str
    item_id: str
    interaction_type: InteractionType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class UserPreference(BaseModel):
    user_id: str
    preferences: Dict[str, float]
    confidence: float
    last_updated: datetime
    privacy_budget_remaining: float

class PrivacySettings(BaseModel):
    user_id: str
    allow_personalization: bool = True
    allow_bias_monitoring: bool = True
    allow_ab_testing: bool = True
    data_retention_days: int = 365
    privacy_level: str = "standard"  # strict, standard, relaxed

class BiasMetric(BaseModel):
    metric_name: str
    value: float
    threshold: float
    is_significant: bool
    affected_groups: List[str]

class BiasReport(BaseModel):
    timestamp: datetime
    overall_bias_score: float
    has_significant_bias: bool
    bias_metrics: List[BiasMetric]
    recommendations: List[str]
    affected_user_count: int

class ABTestVariant(BaseModel):
    variant_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    traffic_percentage: float

class ABTest(BaseModel):
    test_id: Optional[str] = None
    name: str
    description: str
    variants: List[ABTestVariant]
    start_date: datetime
    end_date: Optional[datetime] = None
    success_metrics: List[str]
    is_active: bool = True

class RecommendationItem(BaseModel):
    item_id: str
    score: float
    explanation: str
    confidence: float
    category: str
    metadata: Dict[str, Any] = {}

class RecommendationRequest(BaseModel):
    user_id: str
    count: int = 10
    context: Optional[str] = None
    require_explanations: bool = True
    filter_categories: Optional[List[str]] = None

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    algorithm_version: str
    privacy_preserved: bool
    ab_test_variant: Optional[str] = None

class AuditEntry(BaseModel):
    user_id: str
    timestamp: datetime
    action: str
    item_ids: List[str]
    algorithm_version: str
    explanation: str
    bias_score: Optional[float] = None
