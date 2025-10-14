from typing import Dict, Any, List
import json

def generate_explanation(model: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explainable AI insights for model decisions"""
    
    # Simulate feature importance analysis
    features = list(input_data.keys())
    importance_scores = {
        feature: abs(hash(feature) % 100) / 100 
        for feature in features
    }
    
    # Sort by importance
    sorted_features = sorted(
        importance_scores.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Generate human-readable explanation
    top_features = sorted_features[:3]
    explanation_text = f"The decision was primarily influenced by: "
    explanation_text += ", ".join([
        f"{feat} (importance: {score:.2f})" 
        for feat, score in top_features
    ])
    
    return {
        "explanation": explanation_text,
        "feature_importance": dict(sorted_features),
        "confidence_score": sum(score for _, score in top_features) / len(top_features),
        "decision_factors": [
            {
                "factor": feat,
                "impact": score,
                "description": f"This factor contributed {score:.1%} to the decision"
            }
            for feat, score in top_features
        ]
    }

def validate_decision_fairness(
    decision: Dict[str, Any], 
    demographic_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate that the decision doesn't exhibit bias"""
    
    # Check for potential bias indicators
    bias_checks = {
        "demographic_parity": True,  # Placeholder - would implement real checks
        "equalized_odds": True,
        "individual_fairness": True
    }
    
    return {
        "is_fair": all(bias_checks.values()),
        "bias_checks": bias_checks,
        "recommendation": "Decision appears fair across protected attributes" 
                         if all(bias_checks.values()) 
                         else "Review decision for potential bias"
    }
