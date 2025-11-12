# Production Deployment Guide

## Pre-Deployment Checklist

### Infrastructure
- [ ] Kubernetes cluster provisioned (GKE/EKS/AKS)
- [ ] Container registry configured
- [ ] DNS configured for domains
- [ ] SSL certificates obtained
- [ ] Secrets stored in vault

### Security
- [ ] API keys rotated and secured
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] Container images scanned
- [ ] Security audit completed

### Monitoring
- [ ] Prometheus configured
- [ ] Grafana dashboards created
- [ ] Alerts configured
- [ ] PagerDuty/Oncall integrated
- [ ] Log aggregation setup

## Deployment Steps

### 1. Build and Push Images
```bash
docker build -t your-registry/ai-agent-backend:v1.0 ./backend
docker push your-registry/ai-agent-backend:v1.0
```

### 2. Apply Kubernetes Configs
```bash
kubectl apply -f infrastructure/kubernetes/
```

### 3. Verify Deployment
```bash
kubectl get pods
kubectl get services
kubectl logs -f deployment/ai-agent-backend
```

### 4. Run Smoke Tests
```bash
curl https://your-domain.com/health
curl https://your-domain.com/ready
```

## Rollback Procedure

```bash
kubectl rollout undo deployment/ai-agent-backend
kubectl rollout status deployment/ai-agent-backend
```

## Performance Benchmarks

Expected metrics:
- P50 latency: < 200ms
- P95 latency: < 500ms
- P99 latency: < 1000ms
- Success rate: > 99.5%
- Availability: > 99.9%
