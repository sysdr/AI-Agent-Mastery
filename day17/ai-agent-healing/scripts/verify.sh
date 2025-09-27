#!/bin/bash

# AI Agent Self-Healing System - Verification Script

set -e

echo "🔍 Verifying AI Agent Self-Healing System Installation"
echo "====================================================="
echo ""

ERRORS=0

# Function to check if command exists
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo "✅ $1 is installed"
    else
        echo "❌ $1 is not installed"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1 exists"
    else
        echo "❌ $1 is missing"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check if directory exists
check_directory() {
    if [ -d "$1" ]; then
        echo "✅ $1 directory exists"
    else
        echo "❌ $1 directory is missing"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "🔧 Checking Prerequisites:"
echo "-------------------------"
check_command python
check_command pip
check_command node
check_command npm
check_command curl
echo ""

echo "📁 Checking Project Structure:"
echo "------------------------------"
check_directory "backend"
check_directory "backend/app"
check_directory "backend/app/monitoring"
check_directory "backend/app/recovery"
check_directory "backend/app/health"
check_directory "backend/app/security"
check_directory "frontend"
check_directory "frontend/src"
check_directory "frontend/src/components"
check_directory "tests"
check_directory "scripts"
echo ""

echo "📄 Checking Key Files:"
echo "----------------------"
check_file "backend/requirements.txt"
check_file "backend/app/main.py"
check_file "backend/app/monitoring/anomaly_detector.py"
check_file "backend/app/recovery/auto_recovery.py"
check_file "backend/app/health/monitor.py"
check_file "backend/app/security/incident_manager.py"
check_file "frontend/package.json"
check_file "frontend/src/App.js"
check_file "frontend/src/components/SystemHealth.js"
check_file "frontend/src/components/SecurityMonitor.js"
check_file "Dockerfile"
check_file "docker-compose.yml"
echo ""

echo "🧪 Checking Test Files:"
echo "-----------------------"
check_file "tests/test_anomaly_detector.py"
check_file "tests/test_recovery_system.py"
check_file "tests/test_health_monitor.py"
check_file "tests/test_incident_manager.py"
check_file "frontend/src/App.test.js"
echo ""

echo "📜 Checking Scripts:"
echo "--------------------"
check_file "scripts/build.sh"
check_file "scripts/start.sh"
check_file "scripts/stop.sh"
check_file "scripts/docker-build.sh"
check_file "scripts/demo.sh"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Python virtual environment exists"
    
    # Check if dependencies are installed
    if [ -f "venv/lib/python3.11/site-packages/fastapi" ] || [ -f "venv/lib/python*/site-packages/fastapi" ]; then
        echo "✅ Backend dependencies appear to be installed"
    else
        echo "⚠️  Backend dependencies may not be installed. Run: ./scripts/build.sh"
    fi
else
    echo "⚠️  Python virtual environment not found. Run: ./scripts/build.sh"
fi

# Check if frontend dependencies are installed
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies are installed"
else
    echo "⚠️  Frontend dependencies not installed. Run: ./scripts/build.sh"
fi

echo ""
echo "📊 Verification Summary:"
echo "========================"

if [ $ERRORS -eq 0 ]; then
    echo "🎉 All verification checks passed!"
    echo ""
    echo "Next steps:"
    echo "  1. Set your Gemini API key: export GEMINI_API_KEY=your-key"
    echo "  2. Build the system: ./scripts/build.sh"
    echo "  3. Start the system: ./scripts/start.sh" 
    echo "  4. Run the demo: ./scripts/demo.sh"
else
    echo "❌ $ERRORS verification check(s) failed!"
    echo "Please address the missing components before proceeding."
    exit 1
fi
