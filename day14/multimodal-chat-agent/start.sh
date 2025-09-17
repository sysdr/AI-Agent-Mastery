#!/bin/bash

echo "🚀 Starting Multi-Modal Chat Agent..."

# Start backend
echo "🔧 Starting backend server..."
cd backend
source ../venv/bin/activate
python src/simple_main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Metrics: http://localhost:8000/metrics"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
