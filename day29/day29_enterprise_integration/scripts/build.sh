#!/bin/bash

echo "🔨 Building Enterprise Integration Platform..."

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Backend dependencies installed"

# Frontend setup
cd ../frontend
npm install

echo "✓ Frontend dependencies installed"

echo "✅ Build complete!"
