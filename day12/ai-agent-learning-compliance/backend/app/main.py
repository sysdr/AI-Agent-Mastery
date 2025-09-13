from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional
import json

from .services.preference_learning import PreferenceLearningService
from .services.bias_detection import BiasDetectionService
from .services.ab_testing import ABTestingService
from .services.recommendation import RecommendationService
from .models.schemas import (
    UserInteraction, BiasReport, ABTest, RecommendationRequest, 
    RecommendationResponse, PrivacySettings, UserPreference
)
from .utils.logging_config import setup_logging
from .utils.metrics import MetricsCollector

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services
preference_service = PreferenceLearningService()
bias_service = BiasDetectionService()
ab_service = ABTestingService()
recommendation_service = RecommendationService()
metrics = MetricsCollector()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    logger.info("Starting AI Agent Learning & Compliance Service")
    
    # Initialize services
    await preference_service.initialize()
    await bias_service.initialize()
    await ab_service.initialize()
    await recommendation_service.initialize()
    
    # Start background monitoring
    asyncio.create_task(bias_monitoring_task())
    asyncio.create_task(privacy_budget_task())
    
    yield
    
    logger.info("Shutting down AI Agent Learning & Compliance Service")

app = FastAPI(
    title="AI Agent Learning & Compliance API",
    description="Privacy-preserving user preference learning with bias detection",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background tasks
async def bias_monitoring_task():
    """Continuously monitor for bias in recommendations"""
    while True:
        try:
            bias_report = await bias_service.generate_bias_report()
            if bias_report.has_significant_bias:
                logger.warning(f"Significant bias detected: {bias_report.bias_metrics}")
                # Trigger model retraining
                await preference_service.retrain_with_bias_correction(bias_report)
            
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error(f"Bias monitoring error: {e}")
            await asyncio.sleep(60)

async def privacy_budget_task():
    """Monitor privacy budget usage across users"""
    while True:
        try:
            budget_status = await preference_service.check_privacy_budgets()
            if budget_status['users_near_limit']:
                logger.info(f"Users near privacy limit: {len(budget_status['users_near_limit'])}")
            
            await asyncio.sleep(3600)  # Check every hour
        except Exception as e:
            logger.error(f"Privacy budget monitoring error: {e}")
            await asyncio.sleep(300)

# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "preference_learning": await preference_service.health_check(),
            "bias_detection": await bias_service.health_check(),
            "ab_testing": await ab_service.health_check(),
            "recommendation": await recommendation_service.health_check()
        }
    }

@app.post("/interactions")
async def record_interaction(interaction: UserInteraction, background_tasks: BackgroundTasks):
    """Record user interaction with privacy protection"""
    try:
        # Add interaction to preference learning
        privacy_preserved = await preference_service.add_interaction(interaction)
        
        # Schedule bias check
        background_tasks.add_task(
            bias_service.check_interaction_bias,
            interaction
        )
        
        # Update metrics
        metrics.record_interaction(interaction.interaction_type)
        
        return {
            "status": "success",
            "privacy_budget_remaining": privacy_preserved.remaining_budget,
            "interaction_id": privacy_preserved.interaction_id
        }
    
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")

@app.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    count: int = 10,
    context: Optional[str] = None
) -> RecommendationResponse:
    """Get personalized recommendations with explanations"""
    try:
        request = RecommendationRequest(
            user_id=user_id,
            count=count,
            context=context,
            require_explanations=True
        )
        
        recommendations = await recommendation_service.generate_recommendations(request)
        
        # Check for A/B test assignment
        ab_assignment = await ab_service.get_user_assignment(user_id)
        if ab_assignment:
            recommendations = await ab_service.apply_test_variant(
                recommendations, ab_assignment
            )
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@app.get("/bias-report")
async def get_bias_report(days: int = 7) -> BiasReport:
    """Get bias analysis report"""
    try:
        return await bias_service.generate_comprehensive_report(days)
    except Exception as e:
        logger.error(f"Error generating bias report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate bias report")

@app.post("/ab-tests")
async def create_ab_test(test: ABTest):
    """Create new A/B test"""
    try:
        test_id = await ab_service.create_test(test)
        return {"test_id": test_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating A/B test: {e}")
        raise HTTPException(status_code=500, detail="Failed to create A/B test")

@app.get("/ab-tests/{test_id}/results")
async def get_test_results(test_id: str):
    """Get A/B test results with statistical significance"""
    try:
        results = await ab_service.get_test_results(test_id)
        return results
    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get test results")

@app.get("/privacy-settings/{user_id}")
async def get_privacy_settings(user_id: str) -> PrivacySettings:
    """Get user privacy settings and budget status"""
    try:
        return await preference_service.get_privacy_settings(user_id)
    except Exception as e:
        logger.error(f"Error getting privacy settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get privacy settings")

@app.put("/privacy-settings/{user_id}")
async def update_privacy_settings(user_id: str, settings: PrivacySettings):
    """Update user privacy settings"""
    try:
        await preference_service.update_privacy_settings(user_id, settings)
        return {"status": "updated"}
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update privacy settings")

@app.get("/audit-trail/{user_id}")
async def get_audit_trail(user_id: str, days: int = 30):
    """Get audit trail for user recommendations"""
    try:
        trail = await recommendation_service.get_audit_trail(user_id, days)
        return trail
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audit trail")

@app.get("/metrics")
async def get_metrics():
    """Get system metrics for monitoring"""
    return {
        "interactions_per_hour": metrics.get_interaction_rate(),
        "bias_detection_alerts": metrics.get_bias_alerts(),
        "privacy_budget_usage": metrics.get_privacy_usage(),
        "recommendation_quality": metrics.get_recommendation_metrics(),
        "active_ab_tests": len(await ab_service.get_active_tests())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
