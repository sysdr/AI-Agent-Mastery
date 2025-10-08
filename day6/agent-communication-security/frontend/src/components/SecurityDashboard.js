import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const SecurityDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/security/dashboard');
      setDashboardData(response.data.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading security dashboard...</div>;
  }

  const threatData = dashboardData?.threat_statistics ? [
    { name: 'High Risk', value: dashboardData.threat_statistics.high_threat_detected },
    { name: 'Medium Risk', value: dashboardData.threat_statistics.medium_threat_detected },
    { name: 'Low Risk', value: dashboardData.threat_statistics.low_threat_detected },
  ] : [];

  return (
    <div className="security-dashboard">
      <h2>🛡️ Security Monitoring Dashboard</h2>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>System Health</h3>
          <div className="health-indicator">
            <span className={`status ${dashboardData?.system_health || 'unknown'}`}>
              {dashboardData?.system_health || 'Unknown'}
            </span>
          </div>
          <p>Active Agents: {dashboardData?.active_agents || 0}</p>
        </div>

        <div className="dashboard-card">
          <h3>Threat Analysis</h3>
          <div className="threat-stats">
            <p>Total Analyzed: {dashboardData?.threat_statistics?.total_analyzed || 0}</p>
            <p>Avg Threat Score: {dashboardData?.threat_statistics?.avg_threat_score || 0}</p>
          </div>
        </div>

        <div className="dashboard-card chart-card">
          <h3>Threat Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={threatData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="dashboard-card">
          <h3>🚨 Recent Security Alerts</h3>
          <div className="alerts-list">
            {dashboardData?.alerts?.slice(0, 5).map((alert, index) => (
              <div key={index} className="alert-item">
                <span className="alert-type">{alert.type}</span>
                <span className="alert-score">Score: {alert.threat_score?.toFixed(2)}</span>
                <span className="alert-time">
                  {new Date(alert.timestamp * 1000).toLocaleTimeString()}
                </span>
              </div>
            )) || <p>No recent alerts</p>}
          </div>
        </div>

        <div className="dashboard-card audit-card">
          <h3>📋 Audit Log</h3>
          <div className="audit-list">
            {dashboardData?.audit_log?.slice(0, 10).map((entry, index) => (
              <div key={index} className="audit-item">
                <span className="audit-action">{entry.action}</span>
                <span className="audit-agent">{entry.sender} → {entry.receiver}</span>
                <span className="audit-time">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
            )) || <p>No audit entries</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;
