import numpy as np
import json
from typing import Dict, List, Any, Optional
from sklearn.metrics import accuracy_score
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
# import differential_privacy.accounting.rdp.rdp_privacy_accountant as dp  # Not available
from datetime import datetime, timedelta
import redis
import asyncio
from ..models.learning import LearningModel, FeedbackData, BiasMetric, PerformanceMetric
from ..utils.database import get_db_session
from ..utils.privacy import apply_differential_privacy
from ..utils.explainability import generate_explanation

class ProductionLearningService:
    def __init__(self, redis_client: redis.Redis, privacy_epsilon: float = 0.1):
        self.redis = redis_client
        self.privacy_epsilon = privacy_epsilon
        self.current_model = None
        self.bias_threshold = 0.1
        
    async def process_feedback(self, feedback: FeedbackData) -> Dict[str, Any]:
        """Process incoming feedback with privacy protection and bias detection"""
        try:
            # Apply differential privacy
            private_feedback = apply_differential_privacy(
                feedback, self.privacy_epsilon
            )
            
            # Update model incrementally
            update_result = await self._update_model(private_feedback)
            
            # Check for bias
            bias_metrics = await self._detect_bias(private_feedback)
            
            # Generate performance metrics
            performance = await self._track_performance(update_result)
            
            return {
                "status": "success",
                "model_updated": update_result["updated"],
                "bias_detected": any(m["threshold_exceeded"] for m in bias_metrics),
                "performance": performance
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _update_model(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Incrementally update the learning model"""
        async with get_db_session() as db:
            # Get current active model
            current_model = db.query(LearningModel).filter(
                LearningModel.is_active == True
            ).first()
            
            if not current_model:
                # Initialize first model
                current_model = LearningModel(
                    version="v1.0.0",
                    weights={"initial": True},
                    bias_metrics={},
                    performance_score=0.0,
                    is_active=True
                )
                db.add(current_model)
                
            # Simple online learning update (in practice, use more sophisticated algorithms)
            learning_rate = 0.01
            satisfaction = feedback.get("satisfaction_score", 0.0)
            
            # Update weights based on feedback
            current_weights = current_model.weights or {}
            feature_key = f"user_type_{feedback.get('user_type', 'default')}"
            
            if feature_key in current_weights:
                current_weights[feature_key] += learning_rate * satisfaction
            else:
                current_weights[feature_key] = satisfaction * learning_rate
                
            current_model.weights = current_weights
            current_model.performance_score = (
                current_model.performance_score * 0.9 + satisfaction * 0.1
            )
            
            db.commit()
            
            return {"updated": True, "new_score": current_model.performance_score}
    
    async def _detect_bias(self, feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect algorithmic bias across protected attributes"""
        async with get_db_session() as db:
            # Get recent feedback data for bias analysis
            recent_feedback = db.query(FeedbackData).filter(
                FeedbackData.created_at > datetime.utcnow() - timedelta(hours=24)
            ).limit(1000).all()
            
            bias_metrics = []
            protected_attributes = ["age_group", "gender", "location"]
            
            for attr in protected_attributes:
                # Group feedback by protected attribute
                groups = {}
                for fb in recent_feedback:
                    demo_data = fb.demographic_data or {}
                    group = demo_data.get(attr, "unknown")
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(fb.satisfaction_score)
                
                if len(groups) > 1:
                    # Calculate demographic parity
                    group_means = {k: np.mean(v) for k, v in groups.items()}
                    max_diff = max(group_means.values()) - min(group_means.values())
                    
                    threshold_exceeded = max_diff > self.bias_threshold
                    
                    bias_metric = BiasMetric(
                        model_version="current",
                        metric_type="demographic_parity",
                        protected_attribute=attr,
                        metric_value=max_diff,
                        threshold_exceeded=threshold_exceeded
                    )
                    
                    db.add(bias_metric)
                    
                    bias_metrics.append({
                        "attribute": attr,
                        "metric_value": max_diff,
                        "threshold_exceeded": threshold_exceeded
                    })
            
            db.commit()
            return bias_metrics
    
    async def _track_performance(self, update_result: Dict[str, Any]) -> Dict[str, Any]:
        """Track system performance and costs"""
        async with get_db_session() as db:
            # Simulate performance tracking (in practice, use real metrics)
            performance_metric = PerformanceMetric(
                model_version="current",
                response_time_ms=np.random.uniform(50, 200),
                api_cost_usd=np.random.uniform(0.01, 0.05),
                memory_usage_mb=np.random.uniform(100, 500),
                accuracy_score=update_result.get("new_score", 0.0)
            )
            
            db.add(performance_metric)
            db.commit()
            
            return {
                "response_time": performance_metric.response_time_ms,
                "cost": performance_metric.api_cost_usd,
                "accuracy": performance_metric.accuracy_score
            }
    
    async def get_model_explanation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explainable AI insights for model decisions"""
        return generate_explanation(self.current_model, input_data)
