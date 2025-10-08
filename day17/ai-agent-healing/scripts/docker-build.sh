#!/bin/bash

# Docker Build Script for AI Agent Self-Healing System

set -e

echo "🐳 Building Docker image for AI Agent Self-Healing System..."

# Build the Docker image
docker build -t ai-agent-healing:latest .

echo "✅ Docker image built successfully!"
echo ""
echo "To run with Docker:"
echo "  docker run -p 8000:8000 -e GEMINI_API_KEY=your-key ai-agent-healing:latest"
echo ""
echo "To run with Docker Compose:"
echo "  GEMINI_API_KEY=your-key docker-compose up"
