#!/bin/bash

echo "🏗️ Building Advanced Tool Orchestration System"

# Create virtual environment
echo "Creating virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd ../frontend
npm install
npm run build

echo "✅ Build completed successfully!"
