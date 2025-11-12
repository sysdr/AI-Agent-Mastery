from datetime import datetime
from typing import Any, Dict
import re

class DataTransformer:
    """Transform data between modern and legacy formats"""
    
    @staticmethod
    def to_legacy_format(modern_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform modern JSON to legacy format"""
        legacy_data = {}
        
        # Convert camelCase to UPPER_SNAKE_CASE
        for key, value in modern_data.items():
            legacy_key = DataTransformer._camel_to_snake(key).upper()
            
            # Convert data types
            if isinstance(value, bool):
                legacy_data[legacy_key] = "Y" if value else "N"
            elif isinstance(value, datetime):
                legacy_data[legacy_key] = value.strftime("%Y%m%d")
            elif isinstance(value, dict):
                legacy_data[legacy_key] = DataTransformer.to_legacy_format(value)
            else:
                legacy_data[legacy_key] = str(value) if value is not None else ""
        
        return legacy_data
    
    @staticmethod
    def to_modern_format(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform legacy format to modern JSON"""
        modern_data = {}
        
        for key, value in legacy_data.items():
            # Convert UPPER_SNAKE_CASE to camelCase
            modern_key = DataTransformer._snake_to_camel(key.lower())
            
            # Convert data types
            if value in ("Y", "N"):
                modern_data[modern_key] = value == "Y"
            elif isinstance(value, str) and re.match(r'^\d{8}$', value):
                # Attempt to parse dates
                try:
                    modern_data[modern_key] = datetime.strptime(value, "%Y%m%d").isoformat()
                except:
                    modern_data[modern_key] = value
            elif isinstance(value, dict):
                modern_data[modern_key] = DataTransformer.to_modern_format(value)
            else:
                modern_data[modern_key] = value
        
        return modern_data
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case"""
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    
    @staticmethod
    def _snake_to_camel(name: str) -> str:
        """Convert snake_case to camelCase"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

data_transformer = DataTransformer()
