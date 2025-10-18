import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts';
import './SecurityMonitor.css';
import apiService from '../../services/apiService';

const SecurityMonitor = ({ onLogout }) => {
  const [securityMetrics, setSecurityMetrics] = useState(null);
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSecurityData = async () => {
      try {
        const [metricsData, threatsData] = await Promise.all([
          apiService.getSecurityMetrics(),
          apiService.getThreats()
        ]);
        setSecurityMetrics(metricsData);
        setThreats(threatsData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch security data:', error);
        setLoading(false);
      }
    };

    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const formatThreatData = (data) => {
    if (!data) return [];
    return Object.entries(data).map(([type, count]) => ({
      type: type.replace('_', ' ').toUpperCase(),
      count: count
    }));
  };

  const formatTimeData = (data) => {
    if (!data) return [];
    return Object.entries(data).map(([time, count]) => ({
      time: time,
      count: count
    }));
  };

  if (loading) {
    return (
      <div className="security-loading">
        <div className="loading-spinner"></div>
        <p>Loading Security Monitor...</p>
      </div>
    );
  }

  return (
    <div className="security-monitor">
      <header className="security-header">
        <h1>🛡️ Security Monitor</h1>
        <div className="header-controls">
          <span className="security-status active">
            Security Active
          </span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="security-grid">
        {/* Security Metrics Cards */}
        <div className="security-metrics">
          <div className="metric-card threat">
            <h3>Threats Blocked</h3>
            <div className="metric-value">{securityMetrics?.threats_blocked || 0}</div>
          </div>
          
          <div className="metric-card rate-limit">
            <h3>Rate Limits Applied</h3>
            <div className="metric-value">{securityMetrics?.rate_limits_applied || 0}</div>
          </div>
          
          <div className="metric-card auth">
            <h3>Failed Auth Attempts</h3>
            <div className="metric-value">{securityMetrics?.failed_auth_attempts || 0}</div>
          </div>
          
          <div className="metric-card suspicious">
            <h3>Suspicious Requests</h3>
            <div className="metric-value">{securityMetrics?.suspicious_requests || 0}</div>
          </div>
        </div>

        {/* Threat Types Chart */}
        <div className="chart-container">
          <h3>Threat Types Detected</h3>
          <BarChart width={600} height={300} data={formatThreatData(securityMetrics?.threat_types)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#ef4444" />
          </BarChart>
        </div>

        {/* Threats Over Time */}
        <div className="chart-container">
          <h3>Threats Over Time (Last 24h)</h3>
          <LineChart width={600} height={300} data={formatTimeData(securityMetrics?.threats_over_time)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#ef4444" strokeWidth={2} />
          </LineChart>
        </div>

        {/* Recent Threats */}
        <div className="threats-list">
          <h3>Recent Threats</h3>
          <div className="threats-container">
            {threats.length > 0 ? (
              threats.slice(0, 10).map((threat, index) => (
                <div key={index} className="threat-item">
                  <div className="threat-info">
                    <span className="threat-type">{threat.type}</span>
                    <span className="threat-time">{new Date(threat.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="threat-details">
                    <span className="threat-source">Source: {threat.source_ip}</span>
                    <span className="threat-severity severity-{threat.severity}">{threat.severity}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-threats">
                <p>✅ No recent threats detected</p>
              </div>
            )}
          </div>
        </div>

        {/* Security Policies */}
        <div className="security-policies">
          <h3>Security Policies</h3>
          <div className="policies-grid">
            <div className="policy-item active">
              <span className="policy-name">Rate Limiting</span>
              <span className="policy-status">✅ Active</span>
            </div>
            <div className="policy-item active">
              <span className="policy-name">IP Whitelisting</span>
              <span className="policy-status">✅ Active</span>
            </div>
            <div className="policy-item active">
              <span className="policy-name">SQL Injection Protection</span>
              <span className="policy-status">✅ Active</span>
            </div>
            <div className="policy-item active">
              <span className="policy-name">XSS Protection</span>
              <span className="policy-status">✅ Active</span>
            </div>
            <div className="policy-item active">
              <span className="policy-name">CSRF Protection</span>
              <span className="policy-status">✅ Active</span>
            </div>
            <div className="policy-item active">
              <span className="policy-name">Audit Logging</span>
              <span className="policy-status">✅ Active</span>
            </div>
          </div>
        </div>

        {/* Security Alerts */}
        <div className="security-alerts">
          <h3>Security Alerts</h3>
          <div className="alerts-container">
            <div className="alert-item info">
              <span className="alert-icon">ℹ️</span>
              <span className="alert-message">All security systems operational</span>
            </div>
            <div className="alert-item warning">
              <span className="alert-icon">⚠️</span>
              <span className="alert-message">High request volume detected</span>
            </div>
            <div className="alert-item success">
              <span className="alert-icon">✅</span>
              <span className="alert-message">No critical threats in the last hour</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityMonitor;
