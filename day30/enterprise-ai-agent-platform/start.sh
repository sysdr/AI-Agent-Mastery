#!/bin/bash
set -e

echo "=== Starting Enterprise AI Agent Platform ==="

# Export environment variable
export GEMINI_API_KEY=your-gemini-api-key

# Start with Docker Compose
echo "Starting services with Docker Compose..."
docker-compose up -d

echo ""
echo "=== Services Started Successfully ==="
echo "Frontend Dashboard: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: ./stop.sh"
