#!/bin/bash
# Build script for Secure Document Processing Agent

set -e

echo "🚀 Building Secure Document Processing Agent..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
cd backend && pip install -r requirements.txt && cd ..

# Install Node.js dependencies and build frontend
echo "Installing Node.js dependencies..."
cd frontend
npm install
npm run build
cd ..

# Create required directories
echo "Creating storage directories..."
mkdir -p backend/storage/{documents,metadata,audit}
mkdir -p backend/logs

# Set environment variables
echo "Setting up environment..."
export GEMINI_API_KEY="your-gemini-api-key-here"
export PYTHONPATH="${PWD}/backend:${PYTHONPATH}"

echo "✅ Build completed successfully!"
echo "Next steps:"
echo "1. Set your GEMINI_API_KEY in .env file"
echo "2. Run './start.sh' to start the application"
echo "3. Visit http://localhost:3000 for the frontend"
echo "4. API documentation at http://localhost:8000/docs"
