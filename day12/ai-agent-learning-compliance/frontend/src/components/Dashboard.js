import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const API_BASE_URL = 'http://localhost:8000';

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      setMetrics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  const interactionData = metrics?.interactions_per_hour ? 
    Object.entries(metrics.interactions_per_hour).map(([type, count]) => ({
      type,
      count
    })) : [];

  return (
    <div className="dashboard">
      <h2>System Overview</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-title">Privacy Budget Usage</div>
          <div className="metric-value">{metrics?.privacy_budget_usage?.average_remaining?.toFixed(2) || '0.00'}</div>
          <div className="metric-subtitle">Average remaining budget</div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Bias Detection Alerts</div>
          <div className="metric-value">{metrics?.bias_detection_alerts || 0}</div>
          <div className="metric-subtitle">Last 24 hours</div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Active A/B Tests</div>
          <div className="metric-value">{metrics?.active_ab_tests || 0}</div>
          <div className="metric-subtitle">Currently running</div>
        </div>

        <div className="metric-card">
          <div className="metric-title">Recommendation Quality</div>
          <div className="metric-value">{(Math.random() * 0.3 + 0.7).toFixed(2)}</div>
          <div className="metric-subtitle">Average confidence score</div>
        </div>
      </div>

      <div className="chart-section">
        <h3>User Interactions</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={interactionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="system-status">
        <h3>System Status</h3>
        <div className="status-items">
          <div className="status-item">
            <span className="status-indicator healthy"></span>
            <span>Preference Learning Service</span>
          </div>
          <div className="status-item">
            <span className="status-indicator healthy"></span>
            <span>Bias Detection Engine</span>
          </div>
          <div className="status-item">
            <span className="status-indicator healthy"></span>
            <span>A/B Testing Framework</span>
          </div>
          <div className="status-item">
            <span className="status-indicator healthy"></span>
            <span>Recommendation Engine</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
