import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [businessMetrics, setBusinessMetrics] = useState(null);
  const [chatQuery, setChatQuery] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [healthStatus, setHealthStatus] = useState({ backend: 'unknown' });

  useEffect(() => {
    fetchMetrics();
    checkHealth();
    const interval = setInterval(() => {
      fetchMetrics();
      checkHealth();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const ready = await fetch(`${API_BASE}/ready`);
      setHealthStatus({
        backend: response.ok && ready.ok ? 'healthy' : 'degraded'
      });
    } catch (error) {
      setHealthStatus({ backend: 'down' });
    }
  };

  const fetchMetrics = async () => {
    try {
      const [systemRes, businessRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/metrics/system`),
        fetch(`${API_BASE}/api/v1/metrics/business`)
      ]);
      
      const system = await systemRes.json();
      const business = await businessRes.json();
      
      setSystemMetrics(system);
      setBusinessMetrics(business);
      
      setMetricsHistory(prev => [...prev.slice(-20), {
        time: new Date().toLocaleTimeString(),
        cpu: system.cpu_percent,
        memory: system.memory_percent,
        requests: business.total_requests_today
      }]);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const handleChat = async () => {
    if (!chatQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: chatQuery,
          agent_type: 'production'
        })
      });
      
      const data = await response.json();
      setChatResponse(data.response);
    } catch (error) {
      setChatResponse('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0ea5e9', '#06b6d4', '#3b82f6', '#8b5cf6', '#ef4444', '#f59e0b'];

  return (
    <div className="dashboard">
      <header className="header">
        <h1>🚀 Enterprise AI Agent Platform</h1>
        <div className="health-indicators">
          <span className={`health-badge ${healthStatus.backend}`}>
            Backend: {healthStatus.backend}
          </span>
        </div>
      </header>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>📊 System Resources</h3>
          {systemMetrics && (
            <div className="metrics-display">
              <div className="metric-item">
                <span className="metric-label">CPU Usage</span>
                <span className="metric-value">{systemMetrics.cpu_percent.toFixed(1)}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Memory Usage</span>
                <span className="metric-value">{systemMetrics.memory_percent.toFixed(1)}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Disk Usage</span>
                <span className="metric-value">{systemMetrics.disk_percent.toFixed(1)}%</span>
              </div>
            </div>
          )}
        </div>

        <div className="metric-card">
          <h3>💼 Business Metrics</h3>
          {businessMetrics && (
            <div className="metrics-display">
              <div className="metric-item">
                <span className="metric-label">Total Requests</span>
                <span className="metric-value">{businessMetrics.total_requests_today}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Success Rate</span>
                <span className="metric-value">{businessMetrics.success_rate_percent}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Avg Response Time</span>
                <span className="metric-value">{businessMetrics.average_response_time_ms}ms</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">User Satisfaction</span>
                <span className="metric-value">{businessMetrics.user_satisfaction}/5.0</span>
              </div>
            </div>
          )}
        </div>

        <div className="chart-card">
          <h3>📈 Resource Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metricsHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="cpu" stroke="#10b981" strokeWidth={2} name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#3b82f6" strokeWidth={2} name="Memory %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chat-card">
          <h3>💬 AI Agent Chat</h3>
          <div className="chat-interface">
            <textarea
              value={chatQuery}
              onChange={(e) => setChatQuery(e.target.value)}
              placeholder="Ask the AI agent anything..."
              className="chat-input"
              rows={3}
            />
            <button
              onClick={handleChat}
              disabled={loading}
              className="chat-button"
            >
              {loading ? '⏳ Processing...' : '🚀 Send'}
            </button>
            {chatResponse && (
              <div className="chat-response">
                <strong>Agent Response:</strong>
                <p>{chatResponse}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="footer">
        <p>Production-Ready Enterprise AI Agent Platform | Day 30 Capstone Project</p>
      </footer>
    </div>
  );
}

export default App;
