import asyncio
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PersonalityMonitor:
    def __init__(self):
        # Simplified version without heavy ML dependencies
        self.baseline_responses = {}
        self.response_history = {}
        
    async def validate_response(
        self, 
        session_id: str, 
        response: str, 
        personality_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate response consistency with established personality"""
        
        try:
            # Initialize session tracking
            if session_id not in self.response_history:
                self.response_history[session_id] = []
            
            # Analyze current response
            response_features = self._extract_response_features(response)
            
            # Get baseline for comparison
            baseline = self._get_personality_baseline(session_id, personality_profile)
            
            # Calculate consistency score
            consistency_score = self._calculate_consistency(response_features, baseline)
            
            # Detect anomalies
            anomalies = self._detect_behavioral_anomalies(
                session_id, response_features, baseline
            )
            
            # Update history
            self.response_history[session_id].append({
                "response": response,
                "features": response_features,
                "timestamp": datetime.now().isoformat(),
                "consistency_score": consistency_score
            })
            
            # Keep only recent history
            self._cleanup_old_history(session_id)
            
            return {
                "is_consistent": consistency_score >= 0.7,
                "consistency_score": consistency_score,
                "anomalies": anomalies,
                "personality_drift": len(anomalies) > 2,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Personality validation error: {str(e)}")
            return {
                "is_consistent": True,  # Default to consistent on error
                "consistency_score": 1.0,
                "anomalies": [],
                "personality_drift": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_response_features(self, response: str) -> Dict[str, Any]:
        """Extract personality-relevant features from response"""
        features = {
            "length": len(response),
            "sentence_count": len([s for s in response.split('.') if s.strip()]),
            "word_count": len(response.split()),
            "avg_word_length": float(np.mean([len(word) for word in response.split()])) if response.split() else 0.0,
            "question_count": response.count('?'),
            "exclamation_count": response.count('!'),
            "technical_terms": self._count_technical_terms(response),
            "politeness_markers": self._count_politeness_markers(response),
            "certainty_markers": self._count_certainty_markers(response),
            "embedding": [0.0] * 10  # Simplified embedding as list
        }
        
        return features
    
    def _count_technical_terms(self, text: str) -> int:
        """Count technical terms in response"""
        technical_terms = [
            'api', 'database', 'algorithm', 'architecture', 'framework',
            'implementation', 'optimization', 'scalability', 'microservices',
            'distributed', 'asynchronous', 'kubernetes', 'docker', 'ci/cd'
        ]
        
        return sum(1 for term in technical_terms if term in text.lower())
    
    def _count_politeness_markers(self, text: str) -> int:
        """Count politeness indicators"""
        politeness_markers = [
            'please', 'thank you', 'sorry', 'excuse me', 'if you don\'t mind',
            'would you', 'could you', 'may i', 'i appreciate', 'thanks'
        ]
        
        return sum(1 for marker in politeness_markers if marker in text.lower())
    
    def _count_certainty_markers(self, text: str) -> int:
        """Count certainty/uncertainty markers"""
        certainty_markers = [
            'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
            'without doubt', 'i\'m confident', 'i\'m sure', 'guaranteed'
        ]
        
        uncertainty_markers = [
            'might', 'maybe', 'perhaps', 'possibly', 'could be', 
            'i think', 'i believe', 'seems like', 'appears to'
        ]
        
        certainty_count = sum(1 for marker in certainty_markers if marker in text.lower())
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker in text.lower())
        
        return certainty_count - uncertainty_count  # Net certainty
    
    def _get_semantic_embedding(self, text: str) -> np.ndarray:
        """Get semantic embedding for text - simplified version"""
        # Return a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return np.array([int(b) for b in hash_bytes[:10]]) / 255.0
    
    def _get_personality_baseline(self, session_id: str, personality_profile: Dict) -> Dict[str, Any]:
        """Get or create personality baseline for session"""
        if session_id not in self.baseline_responses:
            # Create baseline from personality profile
            self.baseline_responses[session_id] = self._create_baseline(personality_profile)
        
        return self.baseline_responses[session_id]
    
    def _create_baseline(self, personality_profile: Dict) -> Dict[str, Any]:
        """Create baseline features from personality profile"""
        tone = personality_profile.get("tone", "professional")
        expertise = personality_profile.get("expertise_level", "senior")
        style = personality_profile.get("communication_style", "direct")
        
        baseline = {
            "length": {"min": 100, "max": 300, "avg": 200},
            "technical_terms": {"min": 2, "max": 8, "avg": 5},
            "politeness_markers": {"min": 1, "max": 3, "avg": 2},
            "certainty_markers": {"min": 0, "max": 2, "avg": 1},
            "tone_profile": tone,
            "expertise_profile": expertise,
            "style_profile": style
        }
        
        # Adjust baseline based on personality
        if tone == "friendly":
            baseline["politeness_markers"]["avg"] += 1
        if expertise == "senior":
            baseline["technical_terms"]["avg"] += 2
            baseline["certainty_markers"]["avg"] += 1
        if style == "detailed":
            baseline["length"]["avg"] += 100
        
        return baseline
    
    def _calculate_consistency(self, features: Dict, baseline: Dict) -> float:
        """Calculate consistency score against baseline"""
        scores = []
        
        # Length consistency
        if baseline["length"]["min"] <= features["length"] <= baseline["length"]["max"]:
            scores.append(1.0)
        else:
            deviation = min(
                abs(features["length"] - baseline["length"]["min"]),
                abs(features["length"] - baseline["length"]["max"])
            ) / baseline["length"]["avg"]
            scores.append(max(0.0, 1.0 - deviation))
        
        # Technical terms consistency
        tech_score = 1.0 - abs(features["technical_terms"] - baseline["technical_terms"]["avg"]) / 10
        scores.append(max(0.0, tech_score))
        
        # Politeness consistency
        politeness_score = 1.0 - abs(features["politeness_markers"] - baseline["politeness_markers"]["avg"]) / 5
        scores.append(max(0.0, politeness_score))
        
        # Certainty consistency
        certainty_score = 1.0 - abs(features["certainty_markers"] - baseline["certainty_markers"]["avg"]) / 3
        scores.append(max(0.0, certainty_score))
        
        return float(np.mean(scores))
    
    def _detect_behavioral_anomalies(
        self, 
        session_id: str, 
        current_features: Dict, 
        baseline: Dict
    ) -> List[str]:
        """Detect behavioral anomalies"""
        anomalies = []
        
        # Check recent history for drift
        history = self.response_history.get(session_id, [])
        if len(history) >= 5:
            recent_scores = [entry["consistency_score"] for entry in history[-5:]]
            avg_recent_score = np.mean(recent_scores)
            
            if avg_recent_score < 0.6:
                anomalies.append("consistency_drift")
        
        # Check for sudden changes
        if history:
            last_features = history[-1]["features"]
            
            # Large length change
            if abs(current_features["length"] - last_features["length"]) > 200:
                anomalies.append("length_anomaly")
            
            # Tone shift (technical terms)
            if abs(current_features["technical_terms"] - last_features["technical_terms"]) > 5:
                anomalies.append("tone_shift")
            
            # Politeness change
            if abs(current_features["politeness_markers"] - last_features["politeness_markers"]) > 3:
                anomalies.append("politeness_shift")
        
        return anomalies
    
    def _cleanup_old_history(self, session_id: str):
        """Remove old history entries"""
        if session_id in self.response_history:
            # Keep only last 20 entries
            self.response_history[session_id] = self.response_history[session_id][-20:]
