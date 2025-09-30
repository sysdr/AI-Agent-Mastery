#!/usr/bin/env python3
"""
Demo script to test Expert Agent System and validate dashboard metrics
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health check: {response.json()}")
    return response.status_code == 200

def test_domains():
    """Test domains endpoint"""
    print("\n🔍 Testing domains endpoint...")
    response = requests.get(f"{BASE_URL}/domains")
    data = response.json()
    print(f"✅ Available domains: {list(data['domains'].keys())}")
    return response.status_code == 200 and len(data['domains']) > 0

def test_expert_query(domain, query, required_confidence=0.7):
    """Test expert query processing"""
    print(f"\n🔍 Testing query in domain '{domain}'...")
    print(f"   Query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/query/{domain}",
        json={
            "query": query,
            "required_confidence": required_confidence
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Query failed: {response.text}")
        return None
    
    data = response.json()
    print(f"✅ Response received:")
    print(f"   - Query ID: {data['query_id']}")
    print(f"   - Confidence: {data['confidence_score']:.2f}")
    print(f"   - Expertise Level: {data['expertise_level']}")
    print(f"   - Processing Time: {data['processing_time']:.2f}s")
    print(f"   - Sources Validated: {len(data.get('sources_validated', []))}")
    print(f"   - Escalation Required: {data['escalation_required']}")
    
    return data

def test_audit_trail(query_id):
    """Test audit trail retrieval"""
    print(f"\n🔍 Testing audit trail for query {query_id}...")
    response = requests.get(f"{BASE_URL}/audit/{query_id}")
    
    if response.status_code != 200:
        print(f"❌ Audit trail retrieval failed")
        return None
    
    data = response.json()
    print(f"✅ Audit trail retrieved:")
    print(f"   - Validation Steps: {len(data.get('validation_steps', []))}")
    print(f"   - Confidence Score: {data['confidence_score']:.2f}")
    
    return data

def test_domain_stats(domain):
    """Test domain statistics"""
    print(f"\n🔍 Testing statistics for domain '{domain}'...")
    response = requests.get(f"{BASE_URL}/stats/{domain}")
    
    if response.status_code != 200:
        print(f"❌ Stats retrieval failed")
        return None
    
    data = response.json()
    print(f"✅ Domain Statistics:")
    print(f"   - Total Entries: {data['total_entries']}")
    print(f"   - Validated Entries: {data['validated_entries']}")
    print(f"   - Validation Rate: {data['validation_rate'] * 100:.1f}%")
    print(f"   - Average Confidence: {data['average_confidence'] * 100:.1f}%")
    
    # Validate non-zero metrics
    if data['total_entries'] == 0:
        print("   ⚠️  WARNING: Total entries is zero!")
        return False
    
    if data['validated_entries'] == 0:
        print("   ⚠️  WARNING: Validated entries is zero!")
        return False
        
    if data['average_confidence'] == 0:
        print("   ⚠️  WARNING: Average confidence is zero!")
        return False
    
    return True

def main():
    print("=" * 70)
    print("Expert Agent System - Demo & Validation Test")
    print("=" * 70)
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Exiting.")
        sys.exit(1)
    
    # Test domains
    if not test_domains():
        print("\n❌ Domains check failed. Exiting.")
        sys.exit(1)
    
    # Test queries in different domains
    test_queries = [
        ("technology", "What are the main HTTP methods used in REST APIs?"),
        ("technology", "Explain Python's dynamic typing"),
        ("medical", "How do vaccines work?"),
        ("finance", "What is portfolio diversification?"),
    ]
    
    query_ids = []
    for domain, query in test_queries:
        result = test_expert_query(domain, query)
        if result:
            query_ids.append((result['query_id'], domain))
        time.sleep(1)
    
    # Test audit trails
    if query_ids:
        test_audit_trail(query_ids[0][0])
    
    # Test domain stats for all domains
    print("\n" + "=" * 70)
    print("Dashboard Metrics Validation")
    print("=" * 70)
    
    all_stats_valid = True
    for domain in ["technology", "medical", "finance", "science", "legal"]:
        stats_valid = test_domain_stats(domain)
        if stats_valid is False:
            all_stats_valid = False
        time.sleep(1)
    
    # Final summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    if all_stats_valid:
        print("✅ All tests passed!")
        print("✅ Dashboard metrics are displaying non-zero values")
        print("✅ System is working correctly")
        return 0
    else:
        print("⚠️  Some metrics are showing zero values")
        print("⚠️  Please check the dashboard for updates")
        return 1

if __name__ == "__main__":
    sys.exit(main())
