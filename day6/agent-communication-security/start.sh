#!/bin/bash

echo "🚀 Starting Agent Communication Security System"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis server..."
    redis-server --daemonize yes
    sleep 2
fi

# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
export JWT_SECRET="your-jwt-secret-change-in-production"
export MASTER_KEY="your-master-encryption-key-change-in-production"
export GEMINI_API_KEY="your-gemini-api-key"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "🔗 Backend API: http://localhost:8000"
echo "🌐 Frontend UI: http://localhost:3000"
echo "📊 API Docs: http://localhost:8000/docs"

# Store PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

wait
