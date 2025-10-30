import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import './Dashboard.css';
import apiService from '../../services/apiService';

const Dashboard = ({ onLogout }) => {
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, healthData] = await Promise.all([
          apiService.getMetrics(),
          apiService.getHealth()
        ]);
        setMetrics(metricsData);
        setHealth(healthData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const formatChartData = (data) => {
    if (!data) return [];
    return Object.entries(data).map(([key, value]) => ({
      name: key.replace('/api/', ''),
      value: value
    }));
  };

  const formatStatusCodeData = (data) => {
    if (!data) return [];
    return Object.entries(data).map(([code, count]) => ({
      status: code,
      count: count
    }));
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🚀 AI Gateway Dashboard</h1>
        <div className="header-controls">
          <span className={`status-indicator ${health?.status || 'unknown'}`}>
            {health?.status || 'Unknown'}
          </span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Key Metrics Cards */}
        <div className="metrics-cards">
          <div className="metric-card">
            <h3>Total Requests</h3>
            <div className="metric-value">{metrics?.total_requests || 0}</div>
          </div>
          
          <div className="metric-card">
            <h3>Threats Blocked</h3>
            <div className="metric-value security">{metrics?.security?.threats_blocked || 0}</div>
          </div>
          
          <div className="metric-card">
            <h3>Rate Limits</h3>
            <div className="metric-value warning">{metrics?.security?.rate_limits_applied || 0}</div>
          </div>
          
          <div className="metric-card">
            <h3>Error Rate</h3>
            <div className="metric-value">
              {health?.error_rate ? (health.error_rate * 100).toFixed(2) + '%' : '0%'}
            </div>
          </div>
        </div>

        {/* Request Distribution Chart */}
        <div className="chart-container">
          <h3>Request Distribution by Endpoint</h3>
          <BarChart width={600} height={300} data={formatChartData(metrics?.requests_per_endpoint)}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
            <XAxis dataKey="name" stroke="white" />
            <YAxis stroke="white" />
            <Tooltip />
            <Bar dataKey="value" fill="#8b5cf6" />
          </BarChart>
        </div>

        {/* Status Code Distribution */}
        <div className="chart-container">
          <h3>HTTP Status Codes</h3>
          <BarChart width={600} height={300} data={formatStatusCodeData(metrics?.status_codes)}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.2)" />
            <XAxis dataKey="status" stroke="white" />
            <YAxis stroke="white" />
            <Tooltip />
            <Bar dataKey="count" fill="#06b6d4" />
          </BarChart>
        </div>

        {/* System Info */}
        <div className="system-info">
          <h3>System Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Uptime:</span>
              <span className="info-value">
                {metrics?.uptime_seconds ? Math.floor(metrics.uptime_seconds / 60) : 0} minutes
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Version:</span>
              <span className="info-value">v1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">Environment:</span>
              <span className="info-value">Development</span>
            </div>
          </div>
        </div>

        {/* Security Status */}
        <div className="security-status">
          <h3>🛡️ Security Status</h3>
          <div className="security-grid">
            <div className="security-item good">
              <span>Authentication: ✅ Active</span>
            </div>
            <div className="security-item good">
              <span>Rate Limiting: ✅ Active</span>
            </div>
            <div className="security-item good">
              <span>Threat Detection: ✅ Active</span>
            </div>
            <div className="security-item good">
              <span>Audit Logging: ✅ Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
