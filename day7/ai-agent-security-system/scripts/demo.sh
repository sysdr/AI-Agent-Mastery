#!/bin/bash

echo "🎭 Running AI Agent Security Assessment Demo..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Register test agents
echo "🤖 Registering test agents..."
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "demo_agent_1",
    "capabilities": ["authentication", "data_processing", "security_scanning"],
    "security_level": "high"
  }'

curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "demo_agent_2", 
    "capabilities": ["monitoring", "alerting"],
    "security_level": "medium"
  }'

# Run security scan
echo "🔍 Running security scan..."
curl -X POST http://localhost:8000/api/v1/security/scan

# Get dashboard data
echo "📊 Fetching dashboard data..."
curl -X GET http://localhost:8000/api/v1/metrics/dashboard

echo "✅ Demo completed! Check the dashboard at http://localhost:3000"
