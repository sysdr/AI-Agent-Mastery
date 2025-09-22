#!/bin/bash

echo "🎬 Running Production Orchestration Demo..."

API_BASE="http://localhost:8000"

# Check if system is running
if ! curl -s "$API_BASE/api/system/status" > /dev/null; then
    echo "❌ System not running. Start with './start.sh' first"
    exit 1
fi

echo "✅ System is running!"

# Get system status
echo "📊 System Status:"
curl -s "$API_BASE/api/system/status" | python -m json.tool

echo -e "\n🚀 Creating demo workflow..."

# Create a demo workflow
curl -X POST "$API_BASE/api/workflows" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo_token" \
  -d '{
    "workflow_type": "customer_onboarding",
    "customer_id": "DEMO_CUSTOMER_001",
    "data": {
      "documents": [
        {"id": "doc1", "type": "identity", "name": "passport.pdf"},
        {"id": "doc2", "type": "financial", "name": "bank_statement.pdf"}
      ],
      "consent_granted": true,
      "data_purpose": "account_opening"
    },
    "compliance_level": "standard"
  }' | python -m json.tool

echo -e "\n📋 Current workflows:"
curl -s "$API_BASE/api/workflows" \
  -H "Authorization: Bearer demo_token" | python -m json.tool

echo -e "\n✅ Demo completed! Check the dashboard at http://localhost:3000"
