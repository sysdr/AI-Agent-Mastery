#!/bin/bash
echo "🚀 Starting AI Agent Observability Platform..."

# Start backend
source venv/bin/activate
cd backend
BACKEND_DIR=$(pwd)
export PYTHONPATH="${BACKEND_DIR}/src:${PYTHONPATH}"
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Platform started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Store PIDs for stop script
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

wait
