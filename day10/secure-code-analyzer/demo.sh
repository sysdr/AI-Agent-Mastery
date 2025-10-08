#!/bin/bash

echo "🎯 Running Secure Code Analysis Agent Demo..."

# Check if services are running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running. Please run './start.sh' first"
    exit 1
fi

echo "🔍 Testing security analysis..."

# Test API endpoints
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | jq .

echo "Testing code analysis..."
curl -s -X POST http://localhost:8000/api/security/analyze-code \
  -H "Content-Type: application/json" \
  -d '{"code": "password = \"hardcoded123\"\nquery = \"SELECT * FROM users WHERE id = \" + user_id", "file_path": "demo.py"}' | jq .

echo "✅ Demo completed successfully!"
echo "📊 Visit http://localhost:3000 to see the full dashboard"
