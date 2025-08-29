#!/bin/bash
# Start script for Secure Document Processing Agent

set -e

echo "🚀 Starting Secure Document Processing Agent..."

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "Starting backend server..."
cd backend
export PYTHONPATH="${PWD}:${PYTHONPATH}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend in background
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ Application started successfully!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop or run './stop.sh'"

# Wait for interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
