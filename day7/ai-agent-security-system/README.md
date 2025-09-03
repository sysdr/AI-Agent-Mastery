# AI Agent Security Assessment System

A comprehensive security monitoring and assessment system for AI agent environments.

## Features

- 🔒 **Real-time Security Monitoring**: Continuous monitoring of AI agent activities
- 🛡️ **Penetration Testing**: Automated security vulnerability scanning
- 📊 **Performance Analytics**: System performance and security metrics
- 📝 **Audit Logging**: Cryptographic audit trail with integrity verification
- 🎯 **Threat Detection**: Advanced threat detection and alerting
- 📈 **Dashboard**: Real-time visualization of security metrics

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL (optional, SQLite used by default)
- Redis (optional, in-memory storage used by default)

### Installation

1. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Start the system:**
   ```bash
   ./scripts/start.sh
   ```

3. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development

- **Run tests:**
  ```bash
  ./scripts/test.sh
  ```

- **Run demo:**
  ```bash
  ./scripts/demo.sh
  ```

- **Stop services:**
  ```bash
  ./scripts/stop.sh
  ```

- **Cleanup:**
  ```bash
  ./scripts/cleanup.sh
  ```

## Architecture

### Backend (FastAPI)
- **Security Coordinator**: Manages agent registration and security policies
- **Audit Logger**: Cryptographic audit trail with blockchain-like integrity
- **Penetration Tester**: Automated security vulnerability scanning
- **Performance Monitor**: Real-time system and security metrics

### Frontend (React)
- **Dashboard**: Real-time security metrics visualization
- **Security Status**: Current security posture overview
- **Audit Log**: Searchable audit trail interface
- **Vulnerability Report**: Detailed vulnerability analysis

## Security Features

- **Encrypted State Management**: All sensitive data encrypted at rest
- **Cryptographic Audit Trail**: HMAC-signed audit entries with hash chaining
- **Multi-layered Security Testing**: Authentication, injection, encryption, state manipulation
- **Real-time Threat Detection**: Continuous monitoring with alerting
- **Performance Security**: Resource usage monitoring and anomaly detection

## API Endpoints

### Agent Management
- `POST /api/v1/agents/register` - Register new agent
- `GET /api/v1/security/status` - Get security status

### Security Operations
- `POST /api/v1/security/scan` - Run security scan
- `GET /api/v1/security/vulnerabilities` - Get vulnerability report

### Audit & Monitoring
- `GET /api/v1/audit/entries` - Get audit log entries
- `GET /api/v1/metrics/performance` - Get performance metrics
- `GET /api/v1/metrics/dashboard` - Get comprehensive dashboard data

## Configuration

Environment variables can be set in `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/security_db
REDIS_URL=redis://localhost:6379
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
