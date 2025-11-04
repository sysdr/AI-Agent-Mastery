#!/bin/bash

set -e

echo "=================================="
echo "Building Day 28 DR System"
echo "=================================="

# Create virtual environment
echo "→ Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "→ Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Create necessary directories
echo "→ Creating data directories..."
mkdir -p data/backups data/logs
mkdir -p data/regions/{us-east,eu-west,ap-south}

# Run tests
echo "→ Running backend tests..."
PYTHONPATH=. pytest backend/tests/ -v

# Install frontend dependencies
echo "→ Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Build complete!"
echo ""
echo "To start the system:"
echo "  ./start.sh"
echo ""
echo "To run with Docker:"
echo "  cd docker && docker-compose up --build"
