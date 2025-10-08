#!/bin/bash

echo "🚀 Starting Multi-Agent Security System"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    pkill -f "uvicorn main:app"
    pkill -f "npm start"
    exit 0
}

trap cleanup INT

# Start backend
cd backend
source ../venv/bin/activate
echo "Starting backend server..."
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 5

# Start frontend
cd ../frontend
echo "Starting frontend development server..."
npm start &

echo "✅ Services started!"
echo "📋 Access points:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
