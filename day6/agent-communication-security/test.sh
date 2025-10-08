#!/bin/bash

echo "🧪 Running Agent Communication Security Tests"

# Activate virtual environment
source venv/bin/activate

# Run backend tests
cd backend
pytest tests/ -v
cd ..

# Run frontend tests
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ All tests completed"
