#!/bin/bash
echo "🛑 Stopping AI Security Platform..."

# Kill any running processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"

# Stop Docker services
docker-compose -f docker/docker-compose.yml down

echo "✅ All services stopped"
