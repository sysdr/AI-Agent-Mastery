import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const MetricsDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/metrics');
      const data = await response.json();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading metrics...</div>;
  }

  if (!metrics || metrics.error) {
    return <div className="error">No metrics data available</div>;
  }

  // Prepare data for charts
  const trendData = metrics.trends.cpu_usage.map((cpu, index) => ({
    index: index,
    cpu: (cpu * 100).toFixed(1),
    memory: (metrics.trends.memory_usage[index] * 100).toFixed(1),
    errorRate: (metrics.trends.error_rate[index] * 100).toFixed(2),
    responseTime: (metrics.trends.response_time[index] * 1000).toFixed(0)
  }));

  const systemUsageData = [
    { name: 'CPU', value: metrics.current.system.cpu_usage * 100, color: '#8884d8' },
    { name: 'Memory', value: metrics.current.system.memory_usage * 100, color: '#82ca9d' },
    { name: 'Disk', value: metrics.current.system.disk_usage * 100, color: '#ffc658' }
  ];

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658'];

  return (
    <div className="metrics-dashboard">
      <div className="metrics-summary">
        <div className="summary-card">
          <h3>📊 Performance Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Requests:</span>
              <span className="summary-value">{metrics.summary.total_requests.toLocaleString()}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Errors:</span>
              <span className="summary-value">{metrics.summary.total_errors}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Avg CPU:</span>
              <span className="summary-value">{(metrics.summary.avg_cpu * 100).toFixed(1)}%</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Avg Memory:</span>
              <span className="summary-value">{(metrics.summary.avg_memory * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h4>🖥️ System Resource Usage</h4>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="cpu" stackId="1" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              <Area type="monotone" dataKey="memory" stackId="1" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h4>⚡ Response Time Trend (ms)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="responseTime" stroke="#ff7300" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h4>🚨 Error Rate Trend (%)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="errorRate" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h4>💾 Current System Usage</h4>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={systemUsageData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
              >
                {systemUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detailed-metrics">
        <div className="metrics-table">
          <h4>📋 Current System Metrics</h4>
          <table>
            <tbody>
              <tr>
                <td>CPU Usage</td>
                <td>{(metrics.current.system.cpu_usage * 100).toFixed(1)}%</td>
              </tr>
              <tr>
                <td>Memory Usage</td>
                <td>{(metrics.current.system.memory_usage * 100).toFixed(1)}%</td>
              </tr>
              <tr>
                <td>Disk Usage</td>
                <td>{(metrics.current.system.disk_usage * 100).toFixed(1)}%</td>
              </tr>
              <tr>
                <td>Request Count</td>
                <td>{metrics.current.application.request_count}</td>
              </tr>
              <tr>
                <td>Error Count</td>
                <td>{metrics.current.application.error_count}</td>
              </tr>
              <tr>
                <td>Error Rate</td>
                <td>{(metrics.current.application.error_rate * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Response Time</td>
                <td>{(metrics.current.application.avg_response_time * 1000).toFixed(0)}ms</td>
              </tr>
              <tr>
                <td>Active Connections</td>
                <td>{metrics.current.application.active_connections}</td>
              </tr>
              <tr>
                <td>Auth Failures</td>
                <td>{metrics.current.security.auth_failures}</td>
              </tr>
              <tr>
                <td>Blocked IPs</td>
                <td>{metrics.current.security.blocked_ips}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="metrics-footer">
        <p>Last updated: {new Date(metrics.current.timestamp).toLocaleString()}</p>
        <p>Data collected over the last 10 monitoring cycles</p>
      </div>
    </div>
  );
};

export default MetricsDashboard;
