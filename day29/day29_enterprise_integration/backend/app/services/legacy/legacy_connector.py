import asyncio
import random
from typing import Dict, Any
from datetime import datetime

class LegacySystemConnector:
    """Simulates connection to legacy mainframe system"""
    
    def __init__(self):
        self.is_healthy = True
        self.response_time_ms = 2000  # Simulate slow legacy system
    
    async def query_customer(self, customer_id: str) -> Dict[str, Any]:
        """Query customer data from legacy system"""
        # Simulate slow legacy system
        await asyncio.sleep(self.response_time_ms / 1000)
        
        # Simulate occasional failures
        if not self.is_healthy or random.random() < 0.05:
            raise Exception("Legacy system unavailable")
        
        # Return legacy format data
        return {
            "CUSTOMER_ID": customer_id,
            "FIRST_NAME": "JOHN",
            "LAST_NAME": "DOE",
            "EMAIL_ADDRESS": "john.doe@example.com",
            "ACCOUNT_STATUS": "Y",
            "CREATED_DATE": "20200115",
            "LAST_UPDATED": datetime.utcnow().strftime("%Y%m%d%H%M%S")
        }
    
    async def update_customer(self, customer_id: str, data: Dict[str, Any]) -> bool:
        """Update customer data in legacy system"""
        await asyncio.sleep(self.response_time_ms / 1000)
        
        if not self.is_healthy or random.random() < 0.05:
            raise Exception("Legacy system unavailable")
        
        return True
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Create transaction in legacy system"""
        await asyncio.sleep(self.response_time_ms / 1000)
        
        if not self.is_healthy:
            raise Exception("Legacy system unavailable")
        
        return f"TXN{random.randint(100000, 999999)}"
    
    def set_health(self, healthy: bool):
        """Set system health (for testing)"""
        self.is_healthy = healthy

legacy_connector = LegacySystemConnector()
