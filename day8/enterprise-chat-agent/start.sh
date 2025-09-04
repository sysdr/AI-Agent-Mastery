#!/bin/bash

set -e

echo "🚀 Starting Enterprise Chat Agent..."

# Check if .env has GEMINI_API_KEY
if ! grep -q "GEMINI_API_KEY=.*[^[:space:]]" .env; then
    echo "⚠️  Warning: GEMINI_API_KEY not set in .env file"
    echo "   AI responses will show a placeholder message"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
fi

# Start Docker services
echo "🐳 Starting Docker services..."
cd docker
docker-compose up -d
cd ..

# Start backend
echo "🖥️ Starting backend server..."
source venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend  
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Demo login credentials:"
echo "   Organization: Acme Corp or TechStart Inc" 
echo "   User Type: Demo User, Administrator, or Support Agent"
echo ""
echo "Press Ctrl+C to stop all services"

# Store PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for interrupt
wait
