#!/bin/bash

echo "🐳 Deploying with Docker"

# Build and start services
cd docker
docker-compose up --build -d

echo "✅ Docker deployment completed!"
echo "Services:"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:8000"
echo "- Prometheus: http://localhost:9090"
echo "- Redis: localhost:6379"
