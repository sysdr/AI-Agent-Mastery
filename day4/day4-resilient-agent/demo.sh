#!/bin/bash

echo "🎬 Running Resilient Agent Demo..."

# Test endpoints
echo "📊 Testing health endpoint..."
curl -s http://localhost:8000/health | jq '.'

echo "📊 Testing monitoring status..."
curl -s http://localhost:8000/api/v1/monitoring/status | jq '.'

echo "📊 Testing price scraping..."
curl -s -X POST http://localhost:8000/api/v1/monitoring/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "name": "Demo"}' | jq '.'

echo "✅ Demo completed! Check the dashboard at http://localhost:3000"
