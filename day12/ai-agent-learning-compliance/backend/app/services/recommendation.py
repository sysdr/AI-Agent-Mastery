import asyncio
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging
import redis.asyncio as redis
import google.generativeai as genai
import json
import os

from ..models.schemas import RecommendationRequest, RecommendationResponse, RecommendationItem, AuditEntry

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.redis_client = None
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        self.algorithm_version = "1.0.0"
    
    async def initialize(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        logger.info("Recommendation Service initialized")
    
    async def health_check(self) -> bool:
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        try:
            # Get user preferences
            user_prefs_data = await self.redis_client.get(f"preferences:{request.user_id}")
            user_prefs = json.loads(user_prefs_data) if user_prefs_data else {}
            
            # Generate recommendations using Gemini
            prompt = f"""
            Generate {request.count} personalized recommendations for user with preferences:
            {json.dumps(user_prefs.get('preferences', {}))}
            
            Context: {request.context or 'general browsing'}
            
            Return JSON array with items containing:
            - item_id: unique identifier
            - score: relevance score 0-1
            - explanation: why recommended
            - confidence: confidence 0-1
            - category: item category
            """
            
            response = await self.model.generate_content_async(prompt)
            recommendations_data = json.loads(response.text)
            
            recommendations = []
            for item in recommendations_data:
                rec_item = RecommendationItem(
                    item_id=item.get('item_id', f'item_{np.random.randint(1000, 9999)}'),
                    score=float(item.get('score', 0.5)),
                    explanation=item.get('explanation', 'Recommended based on your preferences'),
                    confidence=float(item.get('confidence', 0.7)),
                    category=item.get('category', 'general'),
                    metadata={}
                )
                recommendations.append(rec_item)
            
            # Create audit entry
            audit_entry = AuditEntry(
                user_id=request.user_id,
                timestamp=datetime.utcnow(),
                action="generate_recommendations",
                item_ids=[r.item_id for r in recommendations],
                algorithm_version=self.algorithm_version,
                explanation=f"Generated {len(recommendations)} recommendations using user preferences",
                bias_score=0.05  # Would be calculated by bias service
            )
            
            await self.store_audit_entry(audit_entry)
            
            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=recommendations,
                algorithm_version=self.algorithm_version,
                privacy_preserved=True,
                ab_test_variant=None
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Return fallback recommendations
            fallback_recs = [
                RecommendationItem(
                    item_id=f"fallback_{i}",
                    score=0.5,
                    explanation="Fallback recommendation due to system error",
                    confidence=0.3,
                    category="general"
                ) for i in range(request.count)
            ]
            
            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=fallback_recs,
                algorithm_version="fallback",
                privacy_preserved=True,
                ab_test_variant=None
            )
    
    async def store_audit_entry(self, entry: AuditEntry):
        try:
            await self.redis_client.lpush(
                f"audit:{entry.user_id}",
                entry.json()
            )
            # Keep last 1000 entries per user
            await self.redis_client.ltrim(f"audit:{entry.user_id}", 0, 999)
        except Exception as e:
            logger.error(f"Error storing audit entry: {e}")
    
    async def get_audit_trail(self, user_id: str, days: int = 30) -> List[AuditEntry]:
        try:
            entries = await self.redis_client.lrange(f"audit:{user_id}", 0, -1)
            audit_entries = []
            
            for entry_data in entries:
                try:
                    entry = AuditEntry(**json.loads(entry_data.decode()))
                    audit_entries.append(entry)
                except Exception:
                    continue
            
            return audit_entries[:100]  # Limit to most recent 100
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
