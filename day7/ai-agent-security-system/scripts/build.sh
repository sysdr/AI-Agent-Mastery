#!/bin/bash

set -e

echo "🔧 Building AI Agent Security Assessment System..."

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "🔨 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Run tests
echo "🧪 Running backend tests..."
source venv/bin/activate
python -m pytest backend/tests/ -v

echo "🧪 Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

# Build frontend
echo "🏗️ Building frontend for production..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
