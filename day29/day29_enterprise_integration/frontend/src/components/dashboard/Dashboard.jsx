import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, Database, Zap, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_requests: 0,
    successful: 0,
    failed: 0,
    average_processing_time_ms: 0
  });
  const [metrics, setMetrics] = useState([]);
  const [legacyHealth, setLegacyHealth] = useState({ healthy: true });

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsData, healthData] = await Promise.all([
        api.getIntegrationStats(),
        api.getLegacyHealth()
      ]);
      setStats(statsData);
      setLegacyHealth(healthData);
      
      // Add to metrics history
      setMetrics(prev => [...prev.slice(-19), {
        time: new Date().toLocaleTimeString(),
        requests: statsData.total_requests,
        responseTime: statsData.average_processing_time_ms
      }]);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const pieData = [
    { name: 'Successful', value: stats.successful, color: '#10b981' },
    { name: 'Failed', value: stats.failed, color: '#ef4444' }
  ];

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card primary">
          <Activity className="stat-icon" />
          <div>
            <div className="stat-value">{stats.total_requests}</div>
            <div className="stat-label">Total Requests</div>
          </div>
        </div>

        <div className="stat-card success">
          <Zap className="stat-icon" />
          <div>
            <div className="stat-value">{stats.successful}</div>
            <div className="stat-label">Successful</div>
          </div>
        </div>

        <div className="stat-card warning">
          <Database className="stat-icon" />
          <div>
            <div className="stat-value">{stats.average_processing_time_ms.toFixed(0)}ms</div>
            <div className="stat-label">Avg Response Time</div>
          </div>
        </div>

        <div className={`stat-card ${legacyHealth.healthy ? 'success' : 'danger'}`}>
          <AlertCircle className="stat-icon" />
          <div>
            <div className="stat-value">{legacyHealth.healthy ? 'Healthy' : 'Down'}</div>
            <div className="stat-label">Legacy System</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Request Volume Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="requests" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Response Time Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="responseTime" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Success vs Failure Rate</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={entry => `${entry.name}: ${entry.value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>System Status</h3>
          <div className="status-list">
            <div className="status-item">
              <span className="status-dot success"></span>
              <span>API Gateway</span>
              <span className="status-value">Operational</span>
            </div>
            <div className="status-item">
              <span className={`status-dot ${legacyHealth.healthy ? 'success' : 'danger'}`}></span>
              <span>Legacy System</span>
              <span className="status-value">{legacyHealth.healthy ? 'Online' : 'Offline'}</span>
            </div>
            <div className="status-item">
              <span className="status-dot success"></span>
              <span>Event Store</span>
              <span className="status-value">Active</span>
            </div>
            <div className="status-item">
              <span className="status-dot success"></span>
              <span>Cache Layer</span>
              <span className="status-value">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
