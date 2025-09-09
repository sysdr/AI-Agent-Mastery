#!/bin/bash

echo "🚀 Starting Secure Code Analysis Agent..."

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Please create backend/.env with your Gemini API key"
    exit 1
fi

# Start backend
echo "Starting backend server..."
cd backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Application started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
