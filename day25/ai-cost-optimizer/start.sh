#!/bin/bash
# AI Cost Optimizer - Start Script

set -e

echo "🚀 Starting AI Agent Cost Optimization Platform..."

# Check for required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY environment variable not set"
    echo "Please set it with: export GEMINI_API_KEY='your-api-key'"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis server..."
    redis-server --daemonize yes --port 6379
    sleep 2
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Start backend in background
echo "Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Application started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    redis-cli shutdown 2>/dev/null || true
    echo "✅ All services stopped"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Wait for services
wait
