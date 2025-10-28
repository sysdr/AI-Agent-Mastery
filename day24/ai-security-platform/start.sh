#!/bin/bash
echo "🚀 Starting AI Security Platform..."

# Kill any existing processes
echo "🛑 Stopping any existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true

# Free up ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start databases with Docker Compose
docker-compose -f docker/docker-compose.yml up -d

echo "⏳ Waiting for databases to be ready..."
sleep 10

# Create database if it doesn't exist
PGPASSWORD=password psql -h localhost -U postgres -d postgres -c "CREATE DATABASE ai_security;" 2>/dev/null || true

echo "✅ Database ready"

# Start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "✅ Backend started on http://localhost:8000"

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Frontend starting on http://localhost:3000"
echo "✅ Platform is ready!"
echo ""
echo "🔑 Demo Login Credentials:"
echo "Email: admin@example.com"
echo "Password: admin123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose -f docker/docker-compose.yml down" EXIT
wait
