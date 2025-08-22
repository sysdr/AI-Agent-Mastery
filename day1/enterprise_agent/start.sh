#!/bin/bash

echo "🚀 Starting Enterprise Agent System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
cd backend
pip install -r requirements/base.txt
cd ..

# Install frontend dependencies
echo "🌐 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    
    # Generate encryption key
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    sed -i "s/ENCRYPTION_KEY=auto-generated/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    
    echo "⚠️  Please update .env file with your Gemini API key"
    echo "💡 Get your API key from: https://makersuite.google.com/app/apikey"
fi

# Source environment variables (skip comments and empty lines)
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Verify setup
echo "🔍 Running setup verification..."
./verify_setup.sh

# Create required directories
mkdir -p backend/data backend/logs

# Start backend server
echo "🔧 Starting backend server..."
cd backend/src
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 8

# Check if backend is healthy
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✅ System started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🛑 To stop: run ./stop.sh"
echo ""

# Wait a bit for frontend to start
sleep 10

# Test the CLI
echo "🧪 Testing CLI functionality..."
cd backend/src
echo "Starting agent..."
python -m cli start
sleep 2

echo "Checking status..."
python -m cli status
sleep 1

echo "Testing chat..."
python -m cli chat "Hello, this is a test message for the enterprise agent!"
sleep 2

echo "Checking logs..."
python -m cli logs | tail -5
sleep 1

echo "Stopping CLI agent..."
python -m cli stop
cd ../..

# Run tests
echo "🧪 Running automated tests..."
cd tests
python -m pytest unit/ -v
python -m pytest integration/ -v
cd ..

# Performance test
echo "⚡ Running basic performance test..."
echo "Testing API response time..."
time curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Performance test message"}' > /dev/null

echo ""
echo "🎉 Setup and testing complete!"
echo "📊 Check the dashboard at http://localhost:3000"
echo "💡 Try the chat interface to interact with your agent"
echo "🔧 Use CLI commands in backend/src/ for advanced operations"
echo ""
echo "🚀 Your enterprise agent is ready for production-style development!"
