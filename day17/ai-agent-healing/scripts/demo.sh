#!/bin/bash

# AI Agent Self-Healing System - Demo Script

set -e

echo "🎭 AI Agent Self-Healing System Demo"
echo "===================================="
echo ""

# Check if system is running
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend not running. Please start the system first:"
    echo "   ./scripts/start.sh"
    exit 1
fi

echo "✅ System is running"
echo ""

# Demo 1: System Health Check
echo "📊 Demo 1: System Health Check"
echo "------------------------------"
echo "Checking system health..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""
sleep 2

# Demo 2: Get Detailed Metrics
echo "📈 Demo 2: Detailed System Metrics"
echo "----------------------------------"
echo "Fetching detailed metrics..."
curl -s http://localhost:8000/metrics | python -m json.tool | head -20
echo "... (truncated)"
echo ""
sleep 2

# Demo 3: Security Status
echo "🔒 Demo 3: Security Status"
echo "-------------------------"
echo "Checking security status..."
curl -s http://localhost:8000/security/status | python -m json.tool
echo ""
sleep 2

# Demo 4: Simulate DDoS Attack
echo "💥 Demo 4: Simulate DDoS Attack"
echo "------------------------------"
echo "Simulating DDoS attack..."
ATTACK_RESULT=$(curl -s -X POST "http://localhost:8000/simulate/attack?attack_type=ddos")
echo $ATTACK_RESULT | python -m json.tool
echo ""
echo "⏳ Waiting for automatic recovery..."
sleep 8

# Demo 5: Check Incident Response
echo "🚨 Demo 5: Check Incident Response" 
echo "---------------------------------"
echo "Checking recent incidents..."
curl -s http://localhost:8000/incidents | python -m json.tool | head -30
echo "... (showing first incident)"
echo ""
sleep 2

# Demo 6: Manual Recovery Trigger
echo "🔧 Demo 6: Manual Recovery Trigger"
echo "---------------------------------"
echo "Triggering manual recovery..."
curl -s -X POST http://localhost:8000/recovery/trigger | python -m json.tool
echo ""
sleep 3

# Demo 7: Final Health Check
echo "💓 Demo 7: Final Health Check"
echo "-----------------------------"
echo "Checking system health after recovery..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""

echo "🎉 Demo completed!"
echo ""
echo "Key Features Demonstrated:"
echo "  ✅ Real-time health monitoring"
echo "  ✅ Security threat detection"  
echo "  ✅ Automatic incident response"
echo "  ✅ Self-healing capabilities"
echo "  ✅ Comprehensive metrics collection"
echo ""
echo "📊 Visit http://localhost:3000 to see the live dashboard!"
