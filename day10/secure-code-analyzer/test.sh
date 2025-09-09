#!/bin/bash

echo "🧪 Running tests for Secure Code Analysis Agent..."

# Activate virtual environment
source venv/bin/activate

# Run backend tests
cd backend
pytest tests/ -v --cov=app
cd ..

# Run frontend tests (if any)
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ All tests completed"
