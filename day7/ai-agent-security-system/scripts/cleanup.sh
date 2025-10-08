#!/bin/bash

echo "🧹 Cleaning up AI Agent Security Assessment System..."

# Stop services first
if [ -f scripts/stop.sh ]; then
    bash scripts/stop.sh
fi

# Remove temporary files
echo "🗑️ Removing temporary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove node_modules and build artifacts
echo "🗑️ Removing Node.js artifacts..."
rm -rf frontend/node_modules
rm -rf frontend/build
rm -rf frontend/.cache

# Remove Python virtual environment
echo "🗑️ Removing Python virtual environment..."
rm -rf venv

# Remove Docker artifacts
echo "🗑️ Removing Docker artifacts..."
if command -v docker-compose &> /dev/null; then
    cd docker
    docker-compose down -v --remove-orphans
    cd ..
fi

# Remove PID files
rm -f backend.pid frontend.pid

# Remove database files
rm -f audit_log.db

echo "✅ Cleanup completed!"
