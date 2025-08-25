#!/bin/bash

echo "🛑 Stopping Secure Tool Integration System..."

# Kill processes
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null  
    rm .frontend.pid
fi

echo "✅ System stopped"
