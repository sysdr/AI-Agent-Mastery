import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../../services/api';

const MonitoringPanel = () => {
  const [legacyHealth, setLegacyHealth] = useState({ healthy: true });
  const [stats, setStats] = useState({});

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [health, statistics] = await Promise.all([
        api.getLegacyHealth(),
        api.getIntegrationStats()
      ]);
      setLegacyHealth(health);
      setStats(statistics);
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
    }
  };

  const toggleLegacyHealth = async () => {
    try {
      const newHealthStatus = !legacyHealth.healthy;
      await api.setLegacyHealth(newHealthStatus);
      // Refresh data to ensure consistency
      const updatedHealth = await api.getLegacyHealth();
      setLegacyHealth(updatedHealth);
    } catch (error) {
      console.error('Failed to toggle health:', error);
      // On error, try to refresh the current state
      try {
        const currentHealth = await api.getLegacyHealth();
        setLegacyHealth(currentHealth);
      } catch (refreshError) {
        console.error('Failed to refresh health status:', refreshError);
      }
    }
  };

  const successRate = stats.total_requests > 0 
    ? ((stats.successful / stats.total_requests) * 100).toFixed(1)
    : 0;

  return (
    <div className="monitoring-panel">
      <div className="monitoring-grid">
        <div className="monitor-card">
          <div className="monitor-header">
            <Activity size={24} />
            <h3>Circuit Breaker Status</h3>
          </div>
          <div className="monitor-content">
            <div className="circuit-status">
              <div className="circuit-indicator closed">
                <CheckCircle size={48} />
                <span>CLOSED</span>
              </div>
              <div className="circuit-info">
                <p>Legacy system is responding normally</p>
                <p>All requests being forwarded</p>
              </div>
            </div>
          </div>
        </div>

        <div className="monitor-card">
          <div className="monitor-header">
            <AlertTriangle size={24} />
            <h3>Rate Limiting</h3>
          </div>
          <div className="monitor-content">
            <div className="rate-limit-info">
              <div className="limit-item">
                <span className="limit-label">Legacy System Limit</span>
                <span className="limit-value">10 req/min</span>
              </div>
              <div className="limit-item">
                <span className="limit-label">Modern API Limit</span>
                <span className="limit-value">1000 req/min</span>
              </div>
              <div className="limit-item">
                <span className="limit-label">Current Load</span>
                <span className="limit-value">{stats.total_requests || 0} requests</span>
              </div>
            </div>
          </div>
        </div>

        <div className="monitor-card">
          <div className="monitor-header">
            <Activity size={24} />
            <h3>System Health</h3>
          </div>
          <div className="monitor-content">
            <div className="health-grid">
              <div className="health-item">
                <div className={`health-dot ${legacyHealth.healthy ? 'healthy' : 'unhealthy'}`}></div>
                <span>Legacy System</span>
                {legacyHealth.healthy ? <CheckCircle className="icon-success" size={20} /> : <XCircle className="icon-danger" size={20} />}
              </div>
              <div className="health-item">
                <div className="health-dot healthy"></div>
                <span>API Gateway</span>
                <CheckCircle className="icon-success" size={20} />
              </div>
              <div className="health-item">
                <div className="health-dot healthy"></div>
                <span>Event Store</span>
                <CheckCircle className="icon-success" size={20} />
              </div>
              <div className="health-item">
                <div className="health-dot healthy"></div>
                <span>Cache Layer</span>
                <CheckCircle className="icon-success" size={20} />
              </div>
            </div>
            <button 
              className={`btn ${legacyHealth.healthy ? 'btn-success' : 'btn-danger'}`} 
              onClick={toggleLegacyHealth}
            >
              {legacyHealth.healthy ? 'Set Legacy System Down (Test)' : 'Set Legacy System Healthy (Test)'}
            </button>
          </div>
        </div>

        <div className="monitor-card">
          <div className="monitor-header">
            <Activity size={24} />
            <h3>Performance Metrics</h3>
          </div>
          <div className="monitor-content">
            <div className="metrics-list">
              <div className="metric-item">
                <span>Success Rate</span>
                <span className="metric-value">{successRate}%</span>
              </div>
              <div className="metric-item">
                <span>Avg Response Time</span>
                <span className="metric-value">{stats.average_processing_time_ms?.toFixed(0) || 0}ms</span>
              </div>
              <div className="metric-item">
                <span>Failed Requests</span>
                <span className="metric-value">{stats.failed || 0}</span>
              </div>
              <div className="metric-item">
                <span>Cache Hit Rate</span>
                <span className="metric-value">87%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonitoringPanel;
