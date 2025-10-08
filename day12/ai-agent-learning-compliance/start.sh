#!/bin/bash
set -e

echo "🚀 Starting AI Agent Learning & Compliance System"

# Start infrastructure
docker-compose up -d

# Activate Python environment
source venv/bin/activate

# Start backend
echo "🚀 Starting backend server..."
cd backend
python -m app.main &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🚀 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; docker-compose down' INT
wait
