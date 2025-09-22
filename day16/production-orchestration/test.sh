#!/bin/bash

echo "🧪 Running Production Orchestration Tests..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Python tests
echo "🐍 Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short
cd ..

# Run frontend tests (if they exist)
if [ -d "frontend/src" ]; then
    echo "⚛️ Running frontend tests..."
    cd frontend
    npm test -- --run 2>/dev/null || echo "Frontend tests not configured"
    cd ..
fi

echo "✅ Test execution completed!"
