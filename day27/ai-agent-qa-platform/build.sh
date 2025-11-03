#!/bin/bash

echo "🏗️  Building QA Automation Platform..."

# Setup Python environment
./scripts/setup_env.sh

# Activate virtual environment
source qa_env/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..

echo "✅ Build completed successfully!"

# Run tests
echo "🧪 Running tests..."
cd backend
python -m pytest tests/ -v
cd ..

echo "🚀 Starting services..."
# Start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "✅ QA Automation Platform is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid
