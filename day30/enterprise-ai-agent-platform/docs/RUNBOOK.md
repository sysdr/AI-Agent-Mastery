# Production Runbook

## Common Scenarios

### High Error Rate
**Symptoms:** Error rate > 1%
**Investigation:**
1. Check Grafana dashboard for error types
2. Review logs: `kubectl logs -f deployment/ai-agent-backend`
3. Check Gemini API status
4. Verify database connectivity

**Resolution:**
- If API rate limit: Implement backoff
- If database issue: Scale read replicas
- If memory leak: Restart affected pods

### High Latency
**Symptoms:** P95 latency > 1s
**Investigation:**
1. Check resource utilization
2. Review slow query log
3. Check cache hit rate
4. Profile slow endpoints

**Resolution:**
- Scale horizontally if CPU high
- Optimize database queries
- Increase cache TTL
- Add CDN for static assets

### Pod Crashes
**Symptoms:** Pods restarting frequently
**Investigation:**
1. Check pod logs before crash
2. Review resource limits
3. Check for OOM kills
4. Verify liveness probe settings

**Resolution:**
- Increase memory limits
- Fix memory leak in code
- Adjust probe thresholds
- Review recent deployments

## Escalation Path

1. On-call engineer (immediate)
2. Team lead (15 minutes)
3. Engineering manager (30 minutes)
4. VP Engineering (1 hour)

## Contact Information

- On-call: oncall@company.com
- Slack: #production-incidents
- PagerDuty: https://company.pagerduty.com
