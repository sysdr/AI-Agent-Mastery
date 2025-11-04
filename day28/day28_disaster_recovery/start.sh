#!/bin/bash

set -e

echo "=================================="
echo "Starting Day 28 DR System"
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Start backend
echo "→ Starting backend server..."
PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
echo "→ Waiting for backend to start..."
sleep 5

# Start frontend
echo "→ Starting frontend..."
cd frontend
BROWSER=none npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System started!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Save PIDs
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for interrupt
wait
