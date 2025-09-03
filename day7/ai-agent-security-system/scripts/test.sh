#!/bin/bash

set -e

echo "🧪 Running AI Agent Security Assessment System Tests..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Run backend tests
echo "🐍 Running Python backend tests..."
source venv/bin/activate
cd backend
python -m pytest tests/ -v --tb=short
cd ..

# Run frontend tests
echo "⚛️ Running React frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false --passWithNoTests
cd ..

echo "✅ All tests completed!"
