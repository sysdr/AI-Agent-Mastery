#!/bin/bash

echo "🎭 Agent Communication Security Demo"

# Check if system is running
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "❌ Backend not running. Please run ./start.sh first"
    exit 1
fi

echo "📡 Testing agent registration..."
AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"agent_id": "demo-agent-001", "permissions": ["read", "write"]}')

AGENT1_TOKEN=$(echo $AGENT1_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "✅ Agent 1 registered"

# Register second agent
AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"agent_id": "demo-agent-002", "permissions": ["read", "write"]}')

AGENT2_TOKEN=$(echo $AGENT2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "✅ Agent 2 registered"

echo "💬 Sending encrypted message..."
curl -s -X POST "http://localhost:8000/message/send" \
    -H "Authorization: Bearer $AGENT1_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"receiver_id": "demo-agent-002", "content": "Hello from Agent 1! This message is encrypted with AES-256.", "type": "text"}' | python3 -c "import sys, json; print('✅ Message sent:', json.load(sys.stdin))"

echo "📨 Receiving messages..."
curl -s -X GET "http://localhost:8000/messages/receive" \
    -H "Authorization: Bearer $AGENT2_TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Messages received:', len(data['messages']))"

echo "🛡️  Checking security dashboard..."
curl -s -X GET "http://localhost:8000/security/dashboard" \
    -H "Authorization: Bearer $AGENT1_TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Dashboard data:', data['data']['system_health'])"

echo ""
echo "🎉 Demo completed successfully!"
echo "🌐 Open http://localhost:3000 to see the full UI"
echo "📊 API Documentation: http://localhost:8000/docs"
