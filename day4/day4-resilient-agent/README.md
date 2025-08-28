# Day 4: Resilient Web Agent

A production-grade price monitoring agent demonstrating enterprise resilience patterns.

## Features

- **Distributed Rate Limiting**: Coordinates across multiple instances using Redis
- **Circuit Breakers**: Fail-fast protection with automatic recovery
- **Secure Sessions**: HTTPOnly cookies with CSRF protection  
- **Content Validation**: Input sanitization and malware detection
- **Real-time Dashboard**: Professional monitoring interface

## Quick Start

```bash
# Install dependencies
./build.sh

# Start Redis
redis-server

# Start services  
./start.sh

# Open dashboard
open http://localhost:3000
```

## Architecture

The agent implements three defensive layers:

1. **Request Control**: Rate limiting prevents overwhelming target websites
2. **Failure Isolation**: Circuit breakers contain failures  
3. **Security Boundaries**: Session management and input validation

## Demo Credentials

- Username: `admin`
- Password: `password`

## Testing

```bash
./test.sh     # Run unit tests
./demo.sh     # API demonstration
```
