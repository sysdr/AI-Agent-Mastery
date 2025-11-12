import React, { useState } from 'react';
import Dashboard from './components/dashboard/Dashboard';
import IntegrationPanel from './components/integration/IntegrationPanel';
import MonitoringPanel from './components/monitoring/MonitoringPanel';
import AuditPanel from './components/audit/AuditPanel';
import './styles/App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'integration', label: 'Integration', icon: '🔄' },
    { id: 'monitoring', label: 'Monitoring', icon: '📈' },
    { id: 'audit', label: 'Audit Logs', icon: '📝' }
  ];

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏢 Enterprise Integration Platform</h1>
        <p className="subtitle">Legacy System Integration & Event Sourcing</p>
      </header>

      <nav className="tab-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'integration' && <IntegrationPanel />}
        {activeTab === 'monitoring' && <MonitoringPanel />}
        {activeTab === 'audit' && <AuditPanel />}
      </main>
    </div>
  );
}

export default App;
