import React, { useState, useEffect } from 'react';
import './App.css';
import SystemHealth from './components/SystemHealth';
import SecurityMonitor from './components/SecurityMonitor';
import IncidentManager from './components/IncidentManager';
import MetricsDashboard from './components/MetricsDashboard';

function App() {
  const [activeTab, setActiveTab] = useState('health');
  const [systemStatus, setSystemStatus] = useState('healthy');

  useEffect(() => {
    // Fetch initial system status
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setSystemStatus(data.status))
      .catch(err => console.error('Failed to fetch system status:', err));
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'healthy': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🛡️ AI Agent Self-Healing System</h1>
          <div className="status-indicator">
            <span 
              className="status-dot"
              style={{ backgroundColor: getStatusColor(systemStatus) }}
            ></span>
            <span className="status-text">{systemStatus.toUpperCase()}</span>
          </div>
        </div>
        
        <nav className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'health' ? 'active' : ''}`}
            onClick={() => setActiveTab('health')}
          >
            💓 System Health
          </button>
          <button 
            className={`nav-tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            🔒 Security Monitor
          </button>
          <button 
            className={`nav-tab ${activeTab === 'incidents' ? 'active' : ''}`}
            onClick={() => setActiveTab('incidents')}
          >
            🚨 Incidents
          </button>
          <button 
            className={`nav-tab ${activeTab === 'metrics' ? 'active' : ''}`}
            onClick={() => setActiveTab('metrics')}
          >
            📊 Metrics
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'health' && <SystemHealth />}
        {activeTab === 'security' && <SecurityMonitor />}
        {activeTab === 'incidents' && <IncidentManager />}
        {activeTab === 'metrics' && <MetricsDashboard />}
      </main>
    </div>
  );
}

export default App;
