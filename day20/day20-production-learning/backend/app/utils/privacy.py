import numpy as np
from typing import Dict, Any
import hashlib
import json

def apply_differential_privacy(data: Dict[str, Any], epsilon: float) -> Dict[str, Any]:
    """Apply differential privacy to sensitive feedback data"""
    # Laplace mechanism for numerical values
    def add_laplace_noise(value: float, sensitivity: float = 1.0) -> float:
        if value is None:
            return None
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    private_data = data.copy()
    
    # Add noise to satisfaction score
    if "satisfaction_score" in private_data:
        private_data["satisfaction_score"] = add_laplace_noise(
            private_data["satisfaction_score"], sensitivity=1.0
        )
    
    # Hash sensitive identifiers
    if "user_id" in private_data:
        private_data["user_id_hash"] = hashlib.sha256(
            private_data["user_id"].encode()
        ).hexdigest()[:16]  # Use hash instead of real ID
        
    return private_data

def check_user_consent(user_id: str, consent_type: str) -> bool:
    """Check if user has given consent for specific data usage"""
    # In practice, query the database for user consent
    # For demo, assume consent is granted
    return True

def anonymize_demographic_data(demo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize demographic data while preserving utility"""
    if not demo_data:
        return {}
    
    anonymized = {}
    
    # Generalize age to age groups
    if "age" in demo_data:
        age = demo_data["age"]
        if age < 25:
            anonymized["age_group"] = "18-24"
        elif age < 35:
            anonymized["age_group"] = "25-34"
        elif age < 45:
            anonymized["age_group"] = "35-44"
        else:
            anonymized["age_group"] = "45+"
    
    # Keep non-sensitive attributes
    for key in ["location", "user_type"]:
        if key in demo_data:
            anonymized[key] = demo_data[key]
    
    return anonymized
