#!/bin/bash

echo "🚀 Starting Enterprise Multi-Agent System..."

# Activate virtual environment
source enterprise_env/bin/activate

# Start backend server
echo "🐍 Starting Python backend..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend development server
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop the system, run ./stop.sh"

# Keep processes running
wait
