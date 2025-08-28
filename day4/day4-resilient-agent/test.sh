#!/bin/bash
set -e

echo "🧪 Running tests for Resilient Agent..."

source venv/bin/activate
cd backend

# Run backend tests
python -m pytest tests/ -v

cd ../frontend

# Run frontend tests
npm test

echo "✅ All tests passed!"
