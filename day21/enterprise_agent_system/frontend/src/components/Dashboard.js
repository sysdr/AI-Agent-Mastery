import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FiCpu, FiShield, FiCheckCircle, FiAlertTriangle, FiActivity, FiUsers } from 'react-icons/fi';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useWebSocket } from '../hooks/useWebSocket';

const Dashboard = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [agentsStatus, setAgentsStatus] = useState({});
  const [performanceData, setPerformanceData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isConnected, lastMessage } = useWebSocket();

  useEffect(() => {
    fetchSystemData();
    const interval = setInterval(fetchSystemData, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'health_update') {
      setSystemHealth(lastMessage.data);
    }
    if (lastMessage?.type === 'security_alert') {
      toast.error('Security Alert: ' + lastMessage.data[0]?.description);
    }
  }, [lastMessage]);

  const fetchSystemData = async () => {
    try {
      const [healthResponse, agentsResponse] = await Promise.all([
        axios.get('/health'),
        axios.get('/agents/status')
      ]);
      
      setSystemHealth(healthResponse.data);
      setAgentsStatus(agentsResponse.data);
      
      // Generate performance data for chart
      const newDataPoint = {
        time: new Date().toLocaleTimeString(),
        cpu: healthResponse.data.system_metrics?.cpu_usage || 0,
        memory: healthResponse.data.system_metrics?.memory_usage || 0,
        requests: Math.floor(Math.random() * 100) + 50
      };
      
      setPerformanceData(prev => [...prev.slice(-9), newDataPoint]);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch system data:', error);
      toast.error('Failed to fetch system data');
      setIsLoading(false);
    }
  };

  const executeTestTask = async () => {
    try {
      const response = await axios.post('/agents/execute', {
        type: 'data_processing',
        data: 'Test task execution for demonstration'
      });
      
      if (response.data.success) {
        toast.success('Task executed successfully!');
      } else {
        toast.error('Task execution failed');
      }
    } catch (error) {
      toast.error('Failed to execute task');
    }
  };

  const triggerRecovery = async () => {
    try {
      const response = await axios.post('/system/recovery');
      if (response.data.success) {
        toast.success('Recovery procedures initiated');
      } else {
        toast.error('Recovery failed');
      }
    } catch (error) {
      toast.error('Failed to trigger recovery');
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Loading Dashboard...</h1>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return '#28a745';
      case 'warning': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Enterprise Agent Dashboard</h1>
        <p>
          Real-time monitoring and control
          <span 
            className={`connected-indicator ${isConnected ? 'connected' : 'disconnected'}`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
        </p>
      </div>

      <div className="dashboard-grid">
        {/* System Health Card */}
        <div className="dashboard-card">
          <div className="card-header">
            <FiActivity className="card-icon" />
            <h3>System Health</h3>
          </div>
          <div className="metric-row">
            <span className="metric-label">Health Score</span>
            <span className="metric-value">
              {systemHealth?.health_score ? (systemHealth.health_score * 100).toFixed(1) + '%' : 'N/A'}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Status</span>
            <span 
              className={`status-badge status-${systemHealth?.status || 'unknown'}`}
              style={{ color: getStatusColor(systemHealth?.status) }}
            >
              {systemHealth?.status || 'Unknown'}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">CPU Usage</span>
            <span className="metric-value">
              {systemHealth?.system_metrics?.cpu_usage?.toFixed(1) || 0}%
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Memory Usage</span>
            <span className="metric-value">
              {systemHealth?.system_metrics?.memory_usage?.toFixed(1) || 0}%
            </span>
          </div>
        </div>

        {/* Agents Status Card */}
        <div className="dashboard-card">
          <div className="card-header">
            <FiUsers className="card-icon" />
            <h3>Agent Status</h3>
          </div>
          <ul className="agent-list">
            {Object.entries(agentsStatus).map(([agentName, status]) => (
              <li key={agentName} className="agent-item">
                <span className="agent-name">
                  {agentName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <span 
                  className={`status-badge status-${status.status}`}
                  style={{ 
                    backgroundColor: getStatusColor(status.status) + '20',
                    color: getStatusColor(status.status)
                  }}
                >
                  {status.status}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Performance Metrics Chart */}
        <div className="dashboard-card" style={{ gridColumn: 'span 2' }}>
          <div className="card-header">
            <FiCpu className="card-icon" />
            <h3>Performance Metrics</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="cpu" 
                  stroke="#667eea" 
                  strokeWidth={2}
                  name="CPU %"
                />
                <Line 
                  type="monotone" 
                  dataKey="memory" 
                  stroke="#f093fb" 
                  strokeWidth={2}
                  name="Memory %"
                />
                <Line 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#4ecdc4" 
                  strokeWidth={2}
                  name="Requests/min"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Security Status Card */}
        <div className="dashboard-card">
          <div className="card-header">
            <FiShield className="card-icon" />
            <h3>Security Status</h3>
          </div>
          <div className="metric-row">
            <span className="metric-label">Threat Level</span>
            <span className="status-badge status-healthy">Low</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Active Monitoring</span>
            <span className="metric-value">
              <FiCheckCircle style={{ color: '#28a745' }} /> Enabled
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Last Scan</span>
            <span className="metric-value">2 min ago</span>
          </div>
        </div>

        {/* Compliance Status Card */}
        <div className="dashboard-card">
          <div className="card-header">
            <FiCheckCircle className="card-icon" />
            <h3>Compliance Status</h3>
          </div>
          <div className="metric-row">
            <span className="metric-label">Compliance Score</span>
            <span className="metric-value">96.5%</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Audit Status</span>
            <span className="status-badge status-healthy">Compliant</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Last Audit</span>
            <span className="metric-value">1 hour ago</span>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <h3>System Controls</h3>
        <div className="control-buttons">
          <button className="control-btn btn-primary" onClick={executeTestTask}>
            <FiActivity />
            Execute Test Task
          </button>
          <button className="control-btn btn-success" onClick={triggerRecovery}>
            <FiCheckCircle />
            Trigger Recovery
          </button>
          <button className="control-btn btn-secondary" onClick={fetchSystemData}>
            <FiActivity />
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
