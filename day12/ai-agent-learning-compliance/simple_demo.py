#!/usr/bin/env python3
import requests
import random
import time

API_BASE_URL = 'http://localhost:8000'

def generate_demo_interactions():
    """Generate demo user interactions quickly"""
    users = [f'demo_user_{i:03d}' for i in range(1, 6)]  # 5 users
    items = [f'item_{cat}_{i}' for cat in ['movie', 'book', 'music'] for i in range(1, 11)]  # 30 items
    interaction_types = ['view', 'click', 'like']
    
    print("Generating demo interactions...")
    
    for i in range(20):  # Generate 20 interactions
        interaction = {
            'user_id': random.choice(users),
            'item_id': random.choice(items),
            'interaction_type': random.choice(interaction_types),
            'context': {
                'age_group': random.choice(['young', 'middle', 'senior']),
                'gender': random.choice(['male', 'female']),
                'location': random.choice(['urban', 'suburban'])
            }
        }
        
        try:
            response = requests.post(f'{API_BASE_URL}/interactions', json=interaction, timeout=2)
            if response.status_code == 200:
                print(f"✓ Added interaction {i+1}/20 for {interaction['user_id']}")
            else:
                print(f"✗ Failed to add interaction: {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(0.05)  # Small delay

if __name__ == "__main__":
    generate_demo_interactions()
    print("Demo data generation completed!")
