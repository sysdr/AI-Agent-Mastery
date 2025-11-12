#!/bin/bash

echo "🚀 Starting Enterprise Integration Platform..."

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Start docker-compose services (PostgreSQL and Redis)
echo "📦 Starting database services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5433 > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Warning: PostgreSQL may not be ready yet"
    fi
    sleep 1
done

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
for i in {1..30}; do
    if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
        echo "✓ Redis is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Warning: Redis may not be ready yet"
    fi
    sleep 1
done

# Start backend
echo "🔧 Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "✓ Backend started (PID: $BACKEND_PID)"

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✓ Frontend started (PID: $FRONTEND_PID)"

echo "✅ Platform running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Save PIDs
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

wait
