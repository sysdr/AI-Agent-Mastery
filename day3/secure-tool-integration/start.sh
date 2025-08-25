#!/bin/bash

echo "🚀 Starting Secure Tool Integration System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Create required directories
mkdir -p ../data/sample ../logs
cd ..

# Create sample files for testing
mkdir -p /tmp/user/documents
echo "Sample document content for testing secure file agent." > /tmp/user/documents/sample.txt
echo "Another test file." > /tmp/user/documents/readme.txt

# Start backend
echo "Starting backend server..."
cd backend
python src/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Install frontend dependencies and start
echo "Starting frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

wait
