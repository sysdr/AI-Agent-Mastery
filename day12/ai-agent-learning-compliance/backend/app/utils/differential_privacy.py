import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon
        self.budget_cost = 0.01  # Cost per interaction
        self.last_noise_magnitude = 0.0
    
    def add_noise_to_interaction(self, interaction):
        """Add Laplacian noise to interaction data"""
        try:
            # Calculate noise scale
            sensitivity = 1.0  # Maximum change one user can cause
            scale = sensitivity / self.epsilon
            
            # Add noise to numerical values in context
            if hasattr(interaction, 'context') and interaction.context:
                noisy_context = self.add_noise_to_dict(interaction.context, scale)
                interaction.context = noisy_context
            
            self.last_noise_magnitude = scale
            return interaction
            
        except Exception as e:
            logger.error(f"Error adding noise: {e}")
            return interaction
    
    def add_noise_to_dict(self, data: Dict[str, Any], scale: float) -> Dict[str, Any]:
        """Add noise to numerical values in dictionary"""
        noisy_data = {}
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                noise = np.random.laplace(0, scale)
                noisy_data[key] = value + noise
            elif isinstance(value, dict):
                noisy_data[key] = self.add_noise_to_dict(value, scale)
            else:
                noisy_data[key] = value
        
        return noisy_data
