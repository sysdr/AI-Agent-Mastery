#!/bin/bash

echo "🛑 Stopping AI Agent Learning & Compliance System"

# Kill Python processes
pkill -f "python -m app.main" || true

# Kill Node processes
pkill -f "npm start" || true
pkill -f "react-scripts start" || true

# Stop Docker services
docker-compose down

echo "✅ System stopped"
