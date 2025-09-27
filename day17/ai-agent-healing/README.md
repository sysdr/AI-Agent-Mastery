# 🛡️ AI Agent Self-Healing System

A production-grade self-healing AI agent system with security monitoring, anomaly detection, and automatic recovery capabilities.

## 🚀 Quick Start

```bash
# 1. Clone and navigate to the project
cd ai-agent-healing

# 2. Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# 3. Build the system
./scripts/build.sh

# 4. Start the system
./scripts/start.sh

# 5. Run the demo
./scripts/demo.sh
```

## 📊 Access Points

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ Architecture

The system consists of four main components:

### 🔍 Anomaly Detection Engine
- Real-time threat correlation using Gemini AI
- Statistical anomaly detection with configurable thresholds
- Security event correlation and analysis
- AI-powered root cause analysis

### ⚡ Auto-Recovery System
- Smart healing with security validation
- Multiple recovery procedures for different failure modes
- Automatic credential rotation and security posture validation
- Recovery history and success tracking

### 💓 Health Monitor
- Real-time system metrics collection
- WebSocket streaming for live updates
- Configurable alert thresholds
- Comprehensive compliance reporting

### 🚨 Incident Manager
- Security incident creation and tracking
- Automated response workflows
- Attack simulation for testing
- Incident timeline and resolution tracking

## 🧪 Testing & Validation

```bash
# Run all tests
./scripts/build.sh

# Verify installation
./scripts/verify.sh

# Run interactive demo
./scripts/demo.sh

# Manual testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/simulate/attack?attack_type=ddos
```

## 🐳 Docker Deployment

```bash
# Build Docker image
./scripts/docker-build.sh

# Run with Docker Compose
GEMINI_API_KEY=your-key docker-compose up
```

## 📈 Key Features

- **Real-time Monitoring**: Live system health tracking with WebSocket updates
- **AI-Powered Detection**: Gemini AI analyzes patterns and correlates security events
- **Automatic Recovery**: Self-healing capabilities with security validation
- **Attack Simulation**: Built-in testing for DDoS, brute force, malware, and data breach scenarios
- **Compliance Ready**: Audit logging and compliance reporting
- **Production Scale**: Designed for high-throughput AI agent systems

## 🔧 Configuration

Key environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PYTHONPATH`: Set to backend directory path

## 📋 API Endpoints

- `GET /health` - System health status
- `GET /metrics` - Detailed system metrics
- `GET /security/status` - Security threat level
- `GET /incidents` - Recent security incidents
- `POST /simulate/attack` - Simulate security attacks
- `POST /recovery/trigger` - Manual recovery trigger
- `WebSocket /ws/monitoring` - Real-time metrics stream

## 🛑 Shutdown

```bash
./scripts/stop.sh
```

## 📚 Development

The system is built with:
- **Backend**: Python FastAPI with async support
- **Frontend**: React with real-time charts
- **AI**: Google Gemini for intelligent analysis
- **Monitoring**: Custom metrics collection and WebSocket streaming
- **Testing**: Pytest for backend, Jest for frontend

## 🚨 Security Note

This system includes attack simulation features for testing purposes. Ensure proper security measures are in place before deploying to production environments.
