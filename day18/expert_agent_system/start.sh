#!/bin/bash

echo "🚀 Starting Expert Agent System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running build first..."
    ./build.sh
fi

# Start backend
source venv/bin/activate
cd backend
echo "Starting backend server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
cd frontend
echo "Starting frontend server..."
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; rm -f backend.pid frontend.pid; exit" INT
wait
