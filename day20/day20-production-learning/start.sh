#!/bin/bash
set -e

echo "🚀 Starting Day 20: Production Learning & Optimization System"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Please create backend/.env file with your GEMINI_API_KEY"
    echo "Example: GEMINI_API_KEY=your_api_key_here"
    exit 1
fi

# Start with Docker Compose
echo "🐳 Starting services with Docker Compose..."
export GEMINI_API_KEY=$(grep GEMINI_API_KEY backend/.env | cut -d '=' -f2)
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -s http://localhost:8000/api/learning/health > /dev/null; then
    echo "✅ Backend service is healthy"
else
    echo "❌ Backend service is not responding"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
fi

echo ""
echo "🎉 System is running!"
echo "📊 Dashboard: http://localhost:3000"
echo "🤖 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Try the chat interface and provide feedback to see online learning in action!"
echo "📈 Monitor bias detection and performance metrics in real-time"
