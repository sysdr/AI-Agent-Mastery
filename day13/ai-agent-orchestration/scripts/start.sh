#!/bin/bash

echo "🚀 Starting Advanced Tool Orchestration System"

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate || source venv/Scripts/activate
python app/main.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ System started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Metrics: http://localhost:8000/metrics"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
