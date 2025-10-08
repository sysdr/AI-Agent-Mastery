import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import redis.asyncio as redis
from scipy import stats
from sklearn.metrics import confusion_matrix
import os

from ..models.schemas import UserInteraction, BiasReport, BiasMetric
from ..utils.fairness_metrics import FairnessCalculator

logger = logging.getLogger(__name__)

class BiasDetectionService:
    def __init__(self):
        self.redis_client = None
        self.fairness_calculator = FairnessCalculator()
        self.bias_threshold = float(os.getenv('BIAS_THRESHOLD', 0.1))
        self.protected_attributes = ['age_group', 'gender', 'ethnicity', 'location']
        
    async def initialize(self):
        """Initialize the service"""
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        logger.info("Bias Detection Service initialized")
    
    async def health_check(self) -> bool:
        """Check service health"""
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def check_interaction_bias(self, interaction: UserInteraction):
        """Check for bias in individual interaction"""
        try:
            # Record interaction for bias analysis
            await self.record_interaction_for_bias_analysis(interaction)
            
            # Trigger real-time bias check if enough data
            recent_interactions = await self.get_recent_interactions(hours=1)
            if len(recent_interactions) >= 100:  # Minimum sample size
                await self.perform_real_time_bias_check(recent_interactions)
                
        except Exception as e:
            logger.error(f"Error checking interaction bias: {e}")
    
    async def record_interaction_for_bias_analysis(self, interaction: UserInteraction):
        """Record interaction data for bias analysis"""
        try:
            # Extract demographic info (in real system, would be properly anonymized)
            demo_info = self.extract_demographic_info(interaction)
            
            bias_record = {
                'user_id': interaction.user_id,
                'item_id': interaction.item_id,
                'interaction_type': interaction.interaction_type.value,
                'timestamp': interaction.timestamp.isoformat(),
                'demographics': demo_info
            }
            
            # Store in Redis for real-time analysis
            await self.redis_client.lpush(
                'bias_analysis_queue',
                str(bias_record)
            )
            
            # Keep only recent data (24 hours)
            await self.redis_client.ltrim('bias_analysis_queue', 0, 10000)
            
        except Exception as e:
            logger.error(f"Error recording for bias analysis: {e}")
    
    def extract_demographic_info(self, interaction: UserInteraction) -> Dict[str, Any]:
        """Extract demographic information from interaction context"""
        # In a real system, this would use proper user demographic data
        # with appropriate privacy protections
        context = interaction.context or {}
        
        # Simulate demographic extraction (replace with real implementation)
        demographics = {
            'age_group': context.get('age_group', 'unknown'),
            'gender': context.get('gender', 'unknown'),
            'ethnicity': context.get('ethnicity', 'unknown'),
            'location': context.get('location', 'unknown')
        }
        
        return demographics
    
    async def get_recent_interactions(self, hours: int = 24) -> List[Dict]:
        """Get recent interactions for bias analysis"""
        try:
            raw_interactions = await self.redis_client.lrange('bias_analysis_queue', 0, -1)
            interactions = []
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            for raw in raw_interactions:
                try:
                    interaction = eval(raw.decode())  # In production, use proper JSON parsing
                    interaction_time = datetime.fromisoformat(interaction['timestamp'])
                    if interaction_time >= cutoff_time:
                        interactions.append(interaction)
                except Exception:
                    continue
            
            return interactions
        except Exception as e:
            logger.error(f"Error getting recent interactions: {e}")
            return []
    
    async def perform_real_time_bias_check(self, interactions: List[Dict]):
        """Perform real-time bias detection on recent interactions"""
        try:
            df = pd.DataFrame(interactions)
            
            bias_detected = False
            bias_details = []
            
            # Check demographic parity
            parity_results = self.check_demographic_parity(df)
            if any(result['is_biased'] for result in parity_results):
                bias_detected = True
                bias_details.extend(parity_results)
            
            # Check equalized odds
            odds_results = self.check_equalized_odds(df)
            if any(result['is_biased'] for result in odds_results):
                bias_detected = True
                bias_details.extend(odds_results)
            
            if bias_detected:
                await self.trigger_bias_alert(bias_details)
                
        except Exception as e:
            logger.error(f"Error in real-time bias check: {e}")
    
    def check_demographic_parity(self, df: pd.DataFrame) -> List[Dict]:
        """Check for demographic parity violations"""
        results = []
        
        try:
            for attr in self.protected_attributes:
                if attr not in df.columns:
                    continue
                
                # Calculate positive outcome rates by group
                groups = df[attr].unique()
                group_rates = {}
                
                for group in groups:
                    if group == 'unknown':
                        continue
                    
                    group_data = df[df[attr] == group]
                    positive_rate = len(group_data[
                        group_data['interaction_type'].isin(['like', 'share', 'purchase'])
                    ]) / len(group_data) if len(group_data) > 0 else 0
                    
                    group_rates[group] = positive_rate
                
                if len(group_rates) >= 2:
                    rates = list(group_rates.values())
                    max_diff = max(rates) - min(rates)
                    
                    is_biased = max_diff > self.bias_threshold
                    
                    results.append({
                        'metric': 'demographic_parity',
                        'attribute': attr,
                        'is_biased': is_biased,
                        'bias_magnitude': max_diff,
                        'group_rates': group_rates,
                        'threshold': self.bias_threshold
                    })
            
        except Exception as e:
            logger.error(f"Error checking demographic parity: {e}")
        
        return results
    
    def check_equalized_odds(self, df: pd.DataFrame) -> List[Dict]:
        """Check for equalized odds violations"""
        results = []
        
        try:
            # Create positive outcome labels
            df['positive_outcome'] = df['interaction_type'].isin(['like', 'share', 'purchase'])
            
            for attr in self.protected_attributes:
                if attr not in df.columns:
                    continue
                
                groups = df[attr].unique()
                if len(groups) < 2:
                    continue
                
                tpr_by_group = {}  # True Positive Rate by group
                fpr_by_group = {}  # False Positive Rate by group
                
                for group in groups:
                    if group == 'unknown':
                        continue
                    
                    group_data = df[df[attr] == group]
                    if len(group_data) < 10:  # Minimum sample size
                        continue
                    
                    # Calculate TPR and FPR (simplified for demo)
                    positives = group_data[group_data['positive_outcome'] == True]
                    negatives = group_data[group_data['positive_outcome'] == False]
                    
                    tpr = len(positives) / len(group_data) if len(group_data) > 0 else 0
                    fpr = len(negatives) / len(group_data) if len(group_data) > 0 else 0
                    
                    tpr_by_group[group] = tpr
                    fpr_by_group[group] = fpr
                
                if len(tpr_by_group) >= 2:
                    tpr_values = list(tpr_by_group.values())
                    fpr_values = list(fpr_by_group.values())
                    
                    tpr_diff = max(tpr_values) - min(tpr_values)
                    fpr_diff = max(fpr_values) - min(fpr_values)
                    
                    is_biased = max(tpr_diff, fpr_diff) > self.bias_threshold
                    
                    results.append({
                        'metric': 'equalized_odds',
                        'attribute': attr,
                        'is_biased': is_biased,
                        'tpr_bias': tpr_diff,
                        'fpr_bias': fpr_diff,
                        'tpr_by_group': tpr_by_group,
                        'fpr_by_group': fpr_by_group
                    })
            
        except Exception as e:
            logger.error(f"Error checking equalized odds: {e}")
        
        return results
    
    async def trigger_bias_alert(self, bias_details: List[Dict]):
        """Trigger alert when bias is detected"""
        try:
            alert = {
                'timestamp': datetime.utcnow().isoformat(),
                'bias_detected': True,
                'details': bias_details,
                'severity': self.calculate_bias_severity(bias_details)
            }
            
            # Store alert
            await self.redis_client.lpush('bias_alerts', str(alert))
            
            # Log critical alerts
            if alert['severity'] == 'critical':
                logger.critical(f"Critical bias detected: {bias_details}")
            else:
                logger.warning(f"Bias detected: {bias_details}")
                
        except Exception as e:
            logger.error(f"Error triggering bias alert: {e}")
    
    def calculate_bias_severity(self, bias_details: List[Dict]) -> str:
        """Calculate severity of detected bias"""
        max_bias = 0.0
        
        for detail in bias_details:
            if 'bias_magnitude' in detail:
                max_bias = max(max_bias, detail['bias_magnitude'])
            if 'tpr_bias' in detail:
                max_bias = max(max_bias, detail['tpr_bias'])
            if 'fpr_bias' in detail:
                max_bias = max(max_bias, detail['fpr_bias'])
        
        if max_bias > 0.3:
            return 'critical'
        elif max_bias > 0.2:
            return 'high'
        elif max_bias > 0.1:
            return 'medium'
        else:
            return 'low'
    
    async def generate_bias_report(self) -> BiasReport:
        """Generate comprehensive bias report"""
        try:
            # Get recent interactions
            interactions = await self.get_recent_interactions(hours=24)
            
            if len(interactions) < 50:
                return BiasReport(
                    timestamp=datetime.utcnow(),
                    overall_bias_score=0.0,
                    has_significant_bias=False,
                    bias_metrics=[],
                    recommendations=[],
                    affected_user_count=0
                )
            
            df = pd.DataFrame(interactions)
            
            # Calculate bias metrics
            bias_metrics = []
            
            # Demographic parity metrics
            parity_results = self.check_demographic_parity(df)
            for result in parity_results:
                if result['is_biased']:
                    metric = BiasMetric(
                        metric_name=f"demographic_parity_{result['attribute']}",
                        value=result['bias_magnitude'],
                        threshold=self.bias_threshold,
                        is_significant=True,
                        affected_groups=list(result['group_rates'].keys())
                    )
                    bias_metrics.append(metric)
            
            # Equalized odds metrics
            odds_results = self.check_equalized_odds(df)
            for result in odds_results:
                if result['is_biased']:
                    metric = BiasMetric(
                        metric_name=f"equalized_odds_{result['attribute']}",
                        value=max(result['tpr_bias'], result['fpr_bias']),
                        threshold=self.bias_threshold,
                        is_significant=True,
                        affected_groups=list(result['tpr_by_group'].keys())
                    )
                    bias_metrics.append(metric)
            
            # Calculate overall bias score
            overall_bias_score = np.mean([m.value for m in bias_metrics]) if bias_metrics else 0.0
            
            # Generate recommendations
            recommendations = self.generate_bias_recommendations(bias_metrics)
            
            # Count affected users
            affected_users = len(df['user_id'].unique()) if bias_metrics else 0
            
            return BiasReport(
                timestamp=datetime.utcnow(),
                overall_bias_score=overall_bias_score,
                has_significant_bias=len(bias_metrics) > 0,
                bias_metrics=bias_metrics,
                recommendations=recommendations,
                affected_user_count=affected_users
            )
            
        except Exception as e:
            logger.error(f"Error generating bias report: {e}")
            return BiasReport(
                timestamp=datetime.utcnow(),
                overall_bias_score=0.0,
                has_significant_bias=False,
                bias_metrics=[],
                recommendations=[f"Error generating report: {str(e)}"],
                affected_user_count=0
            )
    
    def generate_bias_recommendations(self, bias_metrics: List[BiasMetric]) -> List[str]:
        """Generate recommendations to address detected bias"""
        recommendations = []
        
        if not bias_metrics:
            return ["No significant bias detected. Continue monitoring."]
        
        # Group recommendations by type
        demo_parity_issues = [m for m in bias_metrics if 'demographic_parity' in m.metric_name]
        odds_issues = [m for m in bias_metrics if 'equalized_odds' in m.metric_name]
        
        if demo_parity_issues:
            recommendations.append(
                "Implement demographic parity constraints in recommendation algorithm"
            )
            recommendations.append(
                "Increase data collection diversity to balance representation"
            )
        
        if odds_issues:
            recommendations.append(
                "Apply post-processing fairness corrections to equalize outcomes"
            )
            recommendations.append(
                "Review training data for systematic biases in labeling"
            )
        
        # General recommendations
        recommendations.extend([
            "Increase monitoring frequency for affected demographic groups",
            "Implement A/B testing to validate bias mitigation strategies",
            "Review and update fairness thresholds based on business requirements"
        ])
        
        return recommendations
    
    async def generate_comprehensive_report(self, days: int = 7) -> BiasReport:
        """Generate comprehensive bias report over specified time period"""
        try:
            # This would analyze data over the specified time period
            # For now, return daily report
            return await self.generate_bias_report()
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return BiasReport(
                timestamp=datetime.utcnow(),
                overall_bias_score=0.0,
                has_significant_bias=False,
                bias_metrics=[],
                recommendations=[f"Error: {str(e)}"],
                affected_user_count=0
            )
