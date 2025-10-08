import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FairnessCalculator:
    """Calculate various fairness metrics for bias detection"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def demographic_parity(self, predictions: np.ndarray, groups: np.ndarray) -> float:
        """Calculate demographic parity metric"""
        try:
            unique_groups = np.unique(groups)
            group_rates = []
            
            for group in unique_groups:
                group_mask = groups == group
                group_rate = np.mean(predictions[group_mask])
                group_rates.append(group_rate)
            
            if len(group_rates) < 2:
                return 0.0
            
            return max(group_rates) - min(group_rates)
        except Exception as e:
            logger.error(f"Error calculating demographic parity: {e}")
            return 0.0
    
    def equalized_odds(self, predictions: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> Dict[str, float]:
        """Calculate equalized odds metrics"""
        try:
            unique_groups = np.unique(groups)
            tpr_by_group = {}
            fpr_by_group = {}
            
            for group in unique_groups:
                group_mask = groups == group
                group_predictions = predictions[group_mask]
                group_labels = labels[group_mask]
                
                if len(group_predictions) == 0:
                    continue
                
                # Calculate TPR and FPR
                tp = np.sum((group_predictions == 1) & (group_labels == 1))
                fp = np.sum((group_predictions == 1) & (group_labels == 0))
                fn = np.sum((group_predictions == 0) & (group_labels == 1))
                tn = np.sum((group_predictions == 0) & (group_labels == 0))
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
                
                tpr_by_group[group] = tpr
                fpr_by_group[group] = fpr
            
            tpr_values = list(tpr_by_group.values())
            fpr_values = list(fpr_by_group.values())
            
            tpr_diff = max(tpr_values) - min(tpr_values) if tpr_values else 0.0
            fpr_diff = max(fpr_values) - min(fpr_values) if fpr_values else 0.0
            
            return {
                'tpr_difference': tpr_diff,
                'fpr_difference': fpr_diff,
                'max_difference': max(tpr_diff, fpr_diff)
            }
        except Exception as e:
            logger.error(f"Error calculating equalized odds: {e}")
            return {'tpr_difference': 0.0, 'fpr_difference': 0.0, 'max_difference': 0.0}
    
    def statistical_parity(self, predictions: np.ndarray, groups: np.ndarray) -> float:
        """Calculate statistical parity difference"""
        try:
            unique_groups = np.unique(groups)
            group_rates = []
            
            for group in unique_groups:
                group_mask = groups == group
                group_rate = np.mean(predictions[group_mask])
                group_rates.append(group_rate)
            
            if len(group_rates) < 2:
                return 0.0
            
            return max(group_rates) - min(group_rates)
        except Exception as e:
            logger.error(f"Error calculating statistical parity: {e}")
            return 0.0
    
    def equal_opportunity(self, predictions: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> float:
        """Calculate equal opportunity metric"""
        try:
            unique_groups = np.unique(groups)
            tpr_by_group = []
            
            for group in unique_groups:
                group_mask = groups == group
                group_predictions = predictions[group_mask]
                group_labels = labels[group_mask]
                
                if len(group_predictions) == 0:
                    continue
                
                # Calculate TPR for this group
                tp = np.sum((group_predictions == 1) & (group_labels == 1))
                fn = np.sum((group_predictions == 0) & (group_labels == 1))
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                tpr_by_group.append(tpr)
            
            if len(tpr_by_group) < 2:
                return 0.0
            
            return max(tpr_by_group) - min(tpr_by_group)
        except Exception as e:
            logger.error(f"Error calculating equal opportunity: {e}")
            return 0.0
    
    def calculate_all_metrics(self, predictions: np.ndarray, labels: np.ndarray, groups: np.ndarray) -> Dict[str, float]:
        """Calculate all fairness metrics"""
        try:
            metrics = {
                'demographic_parity': self.demographic_parity(predictions, groups),
                'statistical_parity': self.statistical_parity(predictions, groups),
                'equal_opportunity': self.equal_opportunity(predictions, labels, groups)
            }
            
            odds_metrics = self.equalized_odds(predictions, labels, groups)
            metrics.update(odds_metrics)
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating all metrics: {e}")
            return {}
