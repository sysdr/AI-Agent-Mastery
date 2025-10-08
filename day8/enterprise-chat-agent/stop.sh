#!/bin/bash

echo "🛑 Stopping Enterprise Chat Agent..."

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm .backend.pid
fi

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm .frontend.pid
fi

# Stop Docker services
cd docker
docker-compose down
cd ..

echo "✅ All services stopped"
