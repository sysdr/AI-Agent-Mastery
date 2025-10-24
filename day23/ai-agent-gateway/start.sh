#!/bin/bash

echo "🚀 Starting AI Gateway Services"
echo "==============================="

# Start Redis (assuming it's installed)
echo "🔴 Starting Redis..."
redis-server --daemonize yes --port 6379

# Start Python backend
echo "🐍 Starting Python backend..."
source gateway-env/bin/activate
cd backend/src
python main.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 5

# Start React frontend
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

echo "✅ All services started!"
echo ""
echo "Services running:"
echo "- Backend: http://localhost:8080"
echo "- Frontend: http://localhost:3000"
echo "- Redis: localhost:6379"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo "Run './stop.sh' to stop all services"

# Wait for user input
read -p "Press Enter to stop services..."

# Kill processes
kill $BACKEND_PID $FRONTEND_PID
redis-cli shutdown
