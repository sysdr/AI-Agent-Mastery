#!/bin/bash

echo "🧪 Running Multi-Modal Security Agent Tests..."

# Activate virtual environment
source venv/bin/activate

# Run backend tests
echo "🔧 Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short
cd ..

echo "✅ Tests completed!"
