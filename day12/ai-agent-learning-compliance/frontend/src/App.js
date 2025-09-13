import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './components/Dashboard';
import BiasMonitor from './components/BiasMonitor';
import RecommendationTest from './components/RecommendationTest';
import PrivacySettings from './components/PrivacySettings';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy' });
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'bias':
        return <BiasMonitor />;
      case 'recommendations':
        return <RecommendationTest />;
      case 'privacy':
        return <PrivacySettings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>AI Agent Learning & Compliance Dashboard</h1>
        <div className="health-indicator">
          <span className={`health-dot ${systemHealth?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
          <span>System {systemHealth?.status || 'checking...'}</span>
        </div>
      </header>

      <nav className="app-nav">
        {['dashboard', 'bias', 'recommendations', 'privacy'].map(tab => (
          <button
            key={tab}
            className={`nav-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
