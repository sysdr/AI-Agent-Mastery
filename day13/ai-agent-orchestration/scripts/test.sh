#!/bin/bash

echo "🧪 Running tests for Advanced Tool Orchestration System"

# Test backend
echo "Testing backend..."
cd backend
source venv/bin/activate || source venv/Scripts/activate
python -m pytest tests/ -v

# Test frontend (if tests exist)
echo "Testing frontend..."
cd ../frontend
if [ -f "src/App.test.js" ]; then
    npm test -- --coverage --watchAll=false
fi

echo "✅ Tests completed!"
