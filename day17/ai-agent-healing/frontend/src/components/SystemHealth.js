import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SystemHealth = () => {
  const [healthData, setHealthData] = useState(null);
  const [realtimeData, setRealtimeData] = useState([]);
  const [wsConnection, setWsConnection] = useState(null);

  useEffect(() => {
    // Initial health data fetch
    fetchHealthData();
    
    // WebSocket connection for real-time data
    const ws = new WebSocket('ws://localhost:8000/ws/monitoring');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setRealtimeData(prev => [...prev.slice(-19), {
        time: new Date(data.timestamp).toLocaleTimeString(),
        cpu: (data.cpu * 100).toFixed(1),
        memory: (data.memory * 100).toFixed(1),
        requests: data.requests,
        responseTime: (data.response_time * 1000).toFixed(0)
      }]);
    };

    ws.onopen = () => setWsConnection(ws);
    ws.onclose = () => setWsConnection(null);

    // Cleanup
    return () => {
      if (ws) ws.close();
    };
  }, []);

  const fetchHealthData = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      setHealthData(data);
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    }
  };

  const triggerRecovery = async () => {
    try {
      await fetch('http://localhost:8000/recovery/trigger', { method: 'POST' });
      alert('Recovery process initiated!');
      setTimeout(fetchHealthData, 2000); // Refresh after 2 seconds
    } catch (error) {
      console.error('Failed to trigger recovery:', error);
    }
  };

  if (!healthData) {
    return <div className="loading">Loading health data...</div>;
  }

  return (
    <div className="system-health">
      <div className="health-overview">
        <div className="health-card">
          <h3>System Status</h3>
          <div className={`status-badge status-${healthData.status}`}>
            {healthData.status.toUpperCase()}
          </div>
          <p>Last Updated: {new Date(healthData.timestamp).toLocaleString()}</p>
        </div>

        <div className="health-card">
          <h3>CPU Usage</h3>
          <div className="metric-value">
            {(healthData.metrics?.system?.cpu_usage * 100 || 0).toFixed(1)}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ 
                width: `${(healthData.metrics?.system?.cpu_usage * 100 || 0)}%`,
                backgroundColor: (healthData.metrics?.system?.cpu_usage || 0) > 0.8 ? '#EF4444' : '#10B981'
              }}
            ></div>
          </div>
        </div>

        <div className="health-card">
          <h3>Memory Usage</h3>
          <div className="metric-value">
            {(healthData.metrics?.system?.memory_usage * 100 || 0).toFixed(1)}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ 
                width: `${(healthData.metrics?.system?.memory_usage * 100 || 0)}%`,
                backgroundColor: (healthData.metrics?.system?.memory_usage || 0) > 0.85 ? '#EF4444' : '#10B981'
              }}
            ></div>
          </div>
        </div>

        <div className="health-card">
          <h3>Error Rate</h3>
          <div className="metric-value">
            {((healthData.metrics?.application?.error_rate || 0) * 100).toFixed(2)}%
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ 
                width: `${(healthData.metrics?.application?.error_rate || 0) * 100 * 10}%`,
                backgroundColor: (healthData.metrics?.application?.error_rate || 0) > 0.05 ? '#EF4444' : '#10B981'
              }}
            ></div>
          </div>
        </div>
      </div>

      {healthData.alerts && healthData.alerts.length > 0 && (
        <div className="alerts-section">
          <h3>🚨 Active Alerts</h3>
          <div className="alerts-list">
            {healthData.alerts.map((alert, index) => (
              <div key={index} className="alert-item">
                {alert}
              </div>
            ))}
          </div>
          <button className="recovery-button" onClick={triggerRecovery}>
            🔧 Trigger Recovery
          </button>
        </div>
      )}

      {realtimeData.length > 0 && (
        <div className="realtime-charts">
          <h3>📈 Real-time Metrics</h3>
          <div className="charts-grid">
            <div className="chart-container">
              <h4>CPU & Memory Usage (%)</h4>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={realtimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cpu" stroke="#8884d8" strokeWidth={2} />
                  <Line type="monotone" dataKey="memory" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-container">
              <h4>Request Count</h4>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={realtimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="requests" stroke="#ffc658" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      <div className="connection-status">
        WebSocket: <span className={wsConnection ? 'connected' : 'disconnected'}>
          {wsConnection ? '🟢 Connected' : '🔴 Disconnected'}
        </span>
      </div>
    </div>
  );
};

export default SystemHealth;
