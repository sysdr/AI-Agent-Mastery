#!/usr/bin/env python3
"""
Demo Test Script for Secure Memory Agent
Tests the complete system functionality and validates dashboard metrics
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print("❌ API Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ API Health Check: ERROR - {e}")
        return False

def create_demo_conversations():
    """Create multiple demo conversations"""
    conversations = []
    
    demo_data = [
        {"user_id": "demo_user_1", "title": "Customer Support Chat"},
        {"user_id": "demo_user_2", "title": "Technical Discussion"},
        {"user_id": "demo_user_3", "title": "General Inquiry"}
    ]
    
    for data in demo_data:
        try:
            response = requests.post(f"{BASE_URL}/memory/conversations", params=data)
            if response.status_code == 200:
                conv = response.json()
                conversations.append(conv)
                print(f"✅ Created conversation: {conv['title']} (ID: {conv['id'][:8]}...)")
            else:
                print(f"❌ Failed to create conversation: {data['title']}")
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
    
    return conversations

def add_demo_messages(conversations):
    """Add various types of demo messages"""
    messages = []
    
    # Messages with PII
    pii_messages = [
        "Hi, I'm Sarah Johnson and my phone number is 555-123-4567",
        "My email address is mike.smith@company.com and I work at TechCorp",
        "Please send the invoice to john.doe@business.net, account #12345"
    ]
    
    # Messages without PII
    clean_messages = [
        "Hello, how can I help you today?",
        "The system is working perfectly",
        "Thank you for your inquiry"
    ]
    
    for i, conv in enumerate(conversations):
        # Add PII message
        if i < len(pii_messages):
            try:
                response = requests.post(f"{BASE_URL}/memory/messages", json={
                    "content": pii_messages[i],
                    "role": "user",
                    "conversation_id": conv['id']
                })
                if response.status_code == 200:
                    msg = response.json()
                    messages.append(msg)
                    print(f"✅ Added PII message to {conv['title']}")
                else:
                    print(f"❌ Failed to add PII message to {conv['title']}")
            except Exception as e:
                print(f"❌ Error adding PII message: {e}")
        
        # Add clean message
        if i < len(clean_messages):
            try:
                response = requests.post(f"{BASE_URL}/memory/messages", json={
                    "content": clean_messages[i],
                    "role": "assistant",
                    "conversation_id": conv['id']
                })
                if response.status_code == 200:
                    msg = response.json()
                    messages.append(msg)
                    print(f"✅ Added clean message to {conv['title']}")
                else:
                    print(f"❌ Failed to add clean message to {conv['title']}")
            except Exception as e:
                print(f"❌ Error adding clean message: {e}")
    
    return messages

def test_dashboard_metrics():
    """Test dashboard metrics after adding data"""
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard")
        if response.status_code == 200:
            metrics = response.json()
            print("\n📊 Dashboard Metrics:")
            print(f"   Conversations: {metrics['conversations']['total']} total, {metrics['conversations']['active']} active")
            print(f"   Messages: {metrics['messages']['total']} total, {metrics['messages']['pii_detected']} with PII")
            print(f"   PII Detection Rate: {metrics['messages']['pii_percentage']:.1f}%")
            print(f"   Security Events (24h): {metrics['security']['events_24h']}")
            print(f"   Total Tokens: {metrics['performance']['total_tokens']}")
            
            # Validate that metrics are not zero
            if metrics['conversations']['total'] > 0 and metrics['messages']['total'] > 0:
                print("✅ Dashboard Metrics: PASSED - Data is being tracked")
                return True
            else:
                print("❌ Dashboard Metrics: FAILED - No data being tracked")
                return False
        else:
            print("❌ Failed to fetch dashboard metrics")
            return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def test_security_events():
    """Test security events endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/analytics/security-events")
        if response.status_code == 200:
            events = response.json()
            print(f"\n🔒 Security Events: {len(events['events'])} events found")
            
            # Count different security levels
            levels = {}
            for event in events['events']:
                level = event['security_level']
                levels[level] = levels.get(level, 0) + 1
            
            for level, count in levels.items():
                print(f"   {level}: {count} events")
            
            if events['events']:
                print("✅ Security Events: PASSED - Events are being logged")
                return True
            else:
                print("❌ Security Events: FAILED - No events found")
                return False
        else:
            print("❌ Failed to fetch security events")
            return False
    except Exception as e:
        print(f"❌ Error testing security events: {e}")
        return False

def main():
    """Run the complete demo test"""
    print("🚀 Starting Secure Memory Agent Demo Test")
    print("=" * 50)
    
    # Test 1: API Health
    if not test_api_health():
        print("❌ Cannot proceed without API access")
        return
    
    print("\n📝 Creating demo conversations...")
    conversations = create_demo_conversations()
    
    if not conversations:
        print("❌ No conversations created, cannot proceed")
        return
    
    print(f"\n💬 Created {len(conversations)} conversations")
    
    print("\n📝 Adding demo messages...")
    messages = add_demo_messages(conversations)
    
    print(f"\n💬 Added {len(messages)} messages")
    
    # Wait a moment for processing
    print("\n⏳ Waiting for data processing...")
    time.sleep(2)
    
    # Test 2: Dashboard Metrics
    print("\n📊 Testing Dashboard Metrics...")
    dashboard_ok = test_dashboard_metrics()
    
    # Test 3: Security Events
    print("\n🔒 Testing Security Events...")
    security_ok = test_security_events()
    
    # Final Results
    print("\n" + "=" * 50)
    print("🎯 Demo Test Results:")
    print(f"   Dashboard Metrics: {'✅ PASSED' if dashboard_ok else '❌ FAILED'}")
    print(f"   Security Events: {'✅ PASSED' if security_ok else '❌ FAILED'}")
    
    if dashboard_ok and security_ok:
        print("\n🎉 All tests PASSED! The system is working correctly.")
        print("🌐 Frontend Dashboard: http://localhost:3000")
        print("🔗 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests FAILED. Please check the logs above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()

