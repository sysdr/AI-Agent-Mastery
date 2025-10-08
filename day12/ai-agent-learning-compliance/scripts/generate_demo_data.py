#!/usr/bin/env python3
import asyncio
import aiohttp
import random
from datetime import datetime, timedelta

API_BASE_URL = 'http://localhost:8000'

async def generate_demo_interactions():
    """Generate demo user interactions"""
    async with aiohttp.ClientSession() as session:
        users = [f'demo_user_{i:03d}' for i in range(1, 51)]
        items = [f'item_{cat}_{i}' for cat in ['movie', 'book', 'music', 'product'] for i in range(1, 101)]
        interaction_types = ['view', 'click', 'like', 'dislike', 'share', 'purchase']
        
        print("Generating demo interactions...")
        
        for _ in range(1000):
            interaction = {
                'user_id': random.choice(users),
                'item_id': random.choice(items),
                'interaction_type': random.choice(interaction_types),
                'context': {
                    'age_group': random.choice(['young', 'middle', 'senior']),
                    'gender': random.choice(['male', 'female', 'other']),
                    'location': random.choice(['urban', 'suburban', 'rural']),
                    'device': random.choice(['mobile', 'desktop', 'tablet'])
                }
            }
            
            try:
                async with session.post(f'{API_BASE_URL}/interactions', json=interaction) as resp:
                    if resp.status == 200:
                        print(f"✓ Added interaction for {interaction['user_id']}")
                    else:
                        print(f"✗ Failed to add interaction: {resp.status}")
            except Exception as e:
                print(f"✗ Error: {e}")
            
            await asyncio.sleep(0.1)  # Rate limiting

if __name__ == "__main__":
    asyncio.run(generate_demo_interactions())
