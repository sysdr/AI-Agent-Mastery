import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
import os

from ..models.schemas import UserInteraction, PrivacySettings, UserPreference, InteractionType
from ..utils.differential_privacy import DifferentialPrivacy
from ..utils.database import get_db_session

logger = logging.getLogger(__name__)

@dataclass
class PrivacyPreservedInteraction:
    interaction_id: str
    remaining_budget: float
    noise_added: float

class PreferenceLearningService:
    def __init__(self):
        self.redis_client = None
        self.privacy_engine = DifferentialPrivacy(epsilon=float(os.getenv('PRIVACY_EPSILON', 1.0)))
        self.user_privacy_budgets = {}
        self.preference_models = {}
        
        # Initialize Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def initialize(self):
        """Initialize the service"""
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        await self.load_existing_preferences()
        logger.info("Preference Learning Service initialized")
    
    async def health_check(self) -> bool:
        """Check service health"""
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def add_interaction(self, interaction: UserInteraction) -> PrivacyPreservedInteraction:
        """Add user interaction with differential privacy"""
        user_id = interaction.user_id
        
        # Check privacy budget
        budget_remaining = await self.check_user_privacy_budget(user_id)
        if budget_remaining <= 0:
            raise ValueError(f"Privacy budget exhausted for user {user_id}")
        
        # Apply differential privacy
        noisy_interaction = self.privacy_engine.add_noise_to_interaction(interaction)
        
        # Update preferences
        await self.update_user_preferences(user_id, noisy_interaction)
        
        # Deduct from privacy budget
        await self.deduct_privacy_budget(user_id, self.privacy_engine.budget_cost)
        
        # Store interaction (privacy-preserved)
        interaction_id = f"{user_id}_{interaction.timestamp.timestamp()}"
        await self.store_interaction(interaction_id, noisy_interaction)
        
        return PrivacyPreservedInteraction(
            interaction_id=interaction_id,
            remaining_budget=budget_remaining - self.privacy_engine.budget_cost,
            noise_added=self.privacy_engine.last_noise_magnitude
        )
    
    async def update_user_preferences(self, user_id: str, interaction: UserInteraction):
        """Update user preference model with new interaction"""
        current_prefs = await self.get_user_preferences(user_id)
        
        # Use Gemini AI to analyze interaction patterns
        prompt = f"""
        Analyze this user interaction and update preferences:
        Current preferences: {json.dumps(current_prefs.preferences if current_prefs else {})}
        New interaction: {interaction.interaction_type} on item {interaction.item_id}
        Context: {interaction.context}
        
        Return updated preferences as JSON with confidence scores.
        Consider interaction strength: view=0.1, click=0.3, like=0.7, dislike=-0.5, share=0.8, purchase=1.0
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            updated_prefs = json.loads(response.text)
            
            # Apply exponential smoothing for preference updates
            if current_prefs:
                alpha = 0.1  # Learning rate
                for category, new_score in updated_prefs.items():
                    old_score = current_prefs.preferences.get(category, 0.0)
                    updated_prefs[category] = alpha * new_score + (1 - alpha) * old_score
            
            # Store updated preferences
            preference = UserPreference(
                user_id=user_id,
                preferences=updated_prefs,
                confidence=self.calculate_preference_confidence(updated_prefs),
                last_updated=datetime.utcnow(),
                privacy_budget_remaining=await self.check_user_privacy_budget(user_id)
            )
            
            await self.store_user_preferences(preference)
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            # Fallback to simple rule-based update
            await self.fallback_preference_update(user_id, interaction)
    
    async def fallback_preference_update(self, user_id: str, interaction: UserInteraction):
        """Fallback preference update using simple rules"""
        interaction_weights = {
            InteractionType.VIEW: 0.1,
            InteractionType.CLICK: 0.3,
            InteractionType.LIKE: 0.7,
            InteractionType.DISLIKE: -0.5,
            InteractionType.SHARE: 0.8,
            InteractionType.PURCHASE: 1.0
        }
        
        # Simple category extraction from item_id (in real system, would be more sophisticated)
        category = interaction.item_id.split('_')[0] if '_' in interaction.item_id else 'general'
        weight = interaction_weights.get(interaction.interaction_type, 0.1)
        
        current_prefs = await self.get_user_preferences(user_id)
        preferences = current_prefs.preferences if current_prefs else {}
        
        preferences[category] = preferences.get(category, 0.0) + weight
        
        preference = UserPreference(
            user_id=user_id,
            preferences=preferences,
            confidence=0.5,  # Lower confidence for fallback
            last_updated=datetime.utcnow(),
            privacy_budget_remaining=await self.check_user_privacy_budget(user_id)
        )
        
        await self.store_user_preferences(preference)
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreference]:
        """Get user preferences from cache/database"""
        try:
            cached = await self.redis_client.get(f"preferences:{user_id}")
            if cached:
                data = json.loads(cached)
                return UserPreference(**data)
            
            # For now, return None (database not implemented)
            return None
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return None
    
    async def store_user_preferences(self, preference: UserPreference):
        """Store user preferences in cache and database"""
        try:
            # Store in Redis cache
            await self.redis_client.setex(
                f"preferences:{preference.user_id}",
                3600,  # 1 hour TTL
                preference.json()
            )
            
            # Database storage not implemented for demo
        except Exception as e:
            logger.error(f"Error storing preferences: {e}")
    
    async def check_user_privacy_budget(self, user_id: str) -> float:
        """Check remaining privacy budget for user"""
        try:
            budget = await self.redis_client.get(f"privacy_budget:{user_id}")
            if budget:
                return float(budget)
            else:
                # Initialize new user budget
                initial_budget = float(os.getenv('PRIVACY_EPSILON', 1.0))
                await self.redis_client.setex(f"privacy_budget:{user_id}", 86400, str(initial_budget))
                return initial_budget
        except Exception as e:
            logger.error(f"Error checking privacy budget: {e}")
            return 0.0
    
    async def deduct_privacy_budget(self, user_id: str, cost: float):
        """Deduct from user's privacy budget"""
        try:
            current_budget = await self.check_user_privacy_budget(user_id)
            new_budget = max(0.0, current_budget - cost)
            await self.redis_client.setex(f"privacy_budget:{user_id}", 86400, str(new_budget))
        except Exception as e:
            logger.error(f"Error deducting privacy budget: {e}")
    
    async def check_privacy_budgets(self) -> Dict[str, Any]:
        """Check privacy budget status across all users"""
        try:
            keys = await self.redis_client.keys("privacy_budget:*")
            users_near_limit = []
            total_users = len(keys)
            
            for key in keys:
                budget = float(await self.redis_client.get(key))
                if budget < 0.1:  # Near exhaustion
                    user_id = key.decode().split(':')[1]
                    users_near_limit.append(user_id)
            
            return {
                "total_users": total_users,
                "users_near_limit": users_near_limit,
                "average_budget_remaining": await self.calculate_average_budget()
            }
        except Exception as e:
            logger.error(f"Error checking privacy budgets: {e}")
            return {"error": str(e)}
    
    async def calculate_average_budget(self) -> float:
        """Calculate average remaining privacy budget"""
        try:
            keys = await self.redis_client.keys("privacy_budget:*")
            if not keys:
                return 0.0
            
            total_budget = 0.0
            for key in keys:
                budget = float(await self.redis_client.get(key))
                total_budget += budget
            
            return total_budget / len(keys)
        except Exception as e:
            logger.error(f"Error calculating average budget: {e}")
            return 0.0
    
    def calculate_preference_confidence(self, preferences: Dict[str, float]) -> float:
        """Calculate confidence in preference model"""
        if not preferences:
            return 0.0
        
        # Simple confidence based on preference strength and consistency
        values = list(preferences.values())
        mean_strength = np.mean(np.abs(values))
        consistency = 1.0 - (np.std(values) / (np.mean(np.abs(values)) + 0.001))
        
        return min(1.0, mean_strength * consistency)
    
    async def retrain_with_bias_correction(self, bias_report):
        """Retrain preferences with bias correction"""
        logger.info("Retraining preferences with bias correction")
        # Implementation would apply fairness constraints to preference learning
        pass
    
    async def get_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Get user privacy settings"""
        try:
            cached = await self.redis_client.get(f"privacy_settings:{user_id}")
            if cached:
                return PrivacySettings(**json.loads(cached))
            
            # Return default settings
            return PrivacySettings(user_id=user_id)
        except Exception as e:
            logger.error(f"Error getting privacy settings: {e}")
            return PrivacySettings(user_id=user_id)
    
    async def update_privacy_settings(self, user_id: str, settings: PrivacySettings):
        """Update user privacy settings"""
        try:
            await self.redis_client.setex(
                f"privacy_settings:{user_id}",
                86400,
                settings.json()
            )
        except Exception as e:
            logger.error(f"Error updating privacy settings: {e}")
    
    async def store_interaction(self, interaction_id: str, interaction: UserInteraction):
        """Store privacy-preserved interaction"""
        try:
            await self.redis_client.setex(
                f"interaction:{interaction_id}",
                3600,
                interaction.json()
            )
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    async def load_existing_preferences(self):
        """Load existing user preferences on startup"""
        try:
            keys = await self.redis_client.keys("preferences:*")
            logger.info(f"Loaded {len(keys)} existing preference models")
        except Exception as e:
            logger.error(f"Error loading existing preferences: {e}")
