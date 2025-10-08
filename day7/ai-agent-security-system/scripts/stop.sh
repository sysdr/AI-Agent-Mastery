#!/bin/bash

echo "🛑 Stopping AI Agent Security Assessment System..."

# Stop Docker Compose if running
if command -v docker-compose &> /dev/null; then
    echo "🐳 Stopping Docker Compose services..."
    cd docker
    docker-compose down
    cd ..
    echo "✅ Docker services stopped"
else
    echo "🔧 Stopping development services..."
    
    # Stop backend if PID file exists
    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "🐍 Stopping backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            rm backend.pid
        fi
    fi
    
    # Stop frontend if PID file exists
    if [ -f frontend.pid ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "⚛️ Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm frontend.pid
        fi
    fi
    
    echo "✅ Development services stopped"
fi

echo "🔒 Security Assessment System stopped!"
