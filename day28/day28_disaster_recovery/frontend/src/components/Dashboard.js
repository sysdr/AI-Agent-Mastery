import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Dashboard.css';

const API_BASE = 'http://localhost:8000';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/metrics/dashboard`);
      setMetrics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const injectFailure = async () => {
    try {
      await axios.post(`${API_BASE}/failover/inject-failure`);
      alert('Failure injected! Watch the system failover automatically.');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const startRecovery = async () => {
    try {
      await axios.post(`${API_BASE}/recovery/start/us-east`);
      alert('Recovery initiated for primary region.');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="header">
          <h1>Loading Dashboard...</h1>
        </div>
      </div>
    );
  }

  const getStateColor = (state) => {
    const colors = {
      'HEALTHY': '#2ecc71',
      'DEGRADED': '#f39c12',
      'CRITICAL': '#e74c3c',
      'FAILOVER_INITIATED': '#3498db',
      'SECONDARY_ACTIVE': '#9b59b6'
    };
    return colors[state] || '#95a5a6';
  };

  return (
    <div className="dashboard">
      <div className="header">
        <h1>🛡️ Disaster Recovery Dashboard</h1>
        <p>Day 28: Real-time monitoring of backup, failover, and recovery systems</p>
      </div>

      <div className="system-status">
        <h2 style={{ marginBottom: '16px', color: '#2c3e50' }}>System Status</h2>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <span className={`status-badge status-${metrics.system_state}`}>
              {metrics.system_state}
            </span>
          </div>
          <div>
            <strong style={{ color: '#2c3e50' }}>Active Region:</strong>{' '}
            <span style={{ 
              padding: '4px 12px', 
              background: '#3498db', 
              color: 'white', 
              borderRadius: '4px',
              fontWeight: '600'
            }}>
              {metrics.active_region}
            </span>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        {Object.entries(metrics.health_metrics || {}).map(([region, health]) => (
          <div key={region} className="metric-card">
            <h3>
              <span className={`health-indicator health-${health.is_healthy ? 'healthy' : 'unhealthy'}`}></span>
              {region.toUpperCase().replace('-', ' ')}
            </h3>
            <div style={{ marginTop: '16px' }}>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#7f8c8d', fontSize: '12px', marginBottom: '4px' }}>Latency</div>
                <div style={{ fontSize: '24px', fontWeight: '700', color: health.latency_ms > 500 ? '#e74c3c' : '#2ecc71' }}>
                  {health.latency_ms.toFixed(0)}ms
                </div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#7f8c8d', fontSize: '12px', marginBottom: '4px' }}>Error Rate</div>
                <div style={{ fontSize: '24px', fontWeight: '700', color: health.error_rate > 0.01 ? '#e74c3c' : '#2ecc71' }}>
                  {(health.error_rate * 100).toFixed(2)}%
                </div>
              </div>
              <div>
                <div style={{ color: '#7f8c8d', fontSize: '12px', marginBottom: '4px' }}>Status</div>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: '600',
                  color: health.is_healthy ? '#2ecc71' : '#e74c3c'
                }}>
                  {health.is_healthy ? '✓ HEALTHY' : '✗ UNHEALTHY'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Backup Statistics</h3>
          {Object.entries(metrics.backup_counts || {}).map(([region, count]) => (
            <div key={region} className="region-status">
              <span className="region-name">{region.toUpperCase()}</span>
              <span className="backup-count">{count} backups</span>
            </div>
          ))}
        </div>

        {metrics.last_failover && (
          <div className="metric-card">
            <h3>Last Failover Event</h3>
            <div style={{ marginTop: '16px' }}>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#7f8c8d', fontSize: '12px' }}>From → To</div>
                <div style={{ color: '#2c3e50', fontWeight: '600' }}>
                  {metrics.last_failover.from_region} → {metrics.last_failover.to_region}
                </div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ color: '#7f8c8d', fontSize: '12px' }}>RTO (Target: 60s)</div>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: '700',
                  color: metrics.last_failover.rto_seconds <= 60 ? '#2ecc71' : '#e74c3c'
                }}>
                  {metrics.last_failover.rto_seconds.toFixed(1)}s
                </div>
              </div>
              <div>
                <div style={{ color: '#7f8c8d', fontSize: '12px' }}>RPO (Target: 30s)</div>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: '700',
                  color: metrics.last_failover.rpo_seconds <= 30 ? '#2ecc71' : '#e74c3c'
                }}>
                  {metrics.last_failover.rpo_seconds}s
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="controls">
        <h3 style={{ marginBottom: '16px', color: '#2c3e50' }}>Chaos Testing Controls</h3>
        <button className="button button-danger" onClick={injectFailure}>
          ⚠️ Inject Failure (Primary Region)
        </button>
        <button className="button button-success" onClick={startRecovery}>
          🔧 Start Recovery
        </button>
      </div>

      <div className="audit-log">
        <h3 style={{ marginBottom: '16px', color: '#2c3e50' }}>Recent Audit Logs</h3>
        {metrics.recent_audit_logs && metrics.recent_audit_logs.length > 0 ? (
          metrics.recent_audit_logs.slice().reverse().map((log, index) => (
            <div key={index} className="log-entry">
              <div className="log-timestamp">
                {new Date(log.timestamp).toLocaleString()}
              </div>
              <div className="log-type">{log.event_type}</div>
              <div className="log-details">
                Region: {log.region} | ID: {log.log_id.substring(0, 8)}...
              </div>
            </div>
          ))
        ) : (
          <p style={{ color: '#7f8c8d' }}>No audit logs yet</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
