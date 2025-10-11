import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard/Dashboard';
import AgentMonitor from './components/AgentMonitor/AgentMonitor';
import NetworkStatus from './components/NetworkStatus/NetworkStatus';
import { fetchNetworkStatus, solveProblem } from './services/api';

function App() {
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchNetworkStatus();
        setNetworkData(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch network data');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, []);

  const handleSolveProblem = async (problem) => {
    try {
      setLoading(true);
      const result = await solveProblem({ problem });
      return result;
    } catch (err) {
      setError('Failed to solve problem');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  if (loading && !networkData) {
    return (
      <div className="app">
        <div className="loading">
          <div className="loader"></div>
          <p>Initializing Distributed Agent Network...</p>
        </div>
      </div>
    );
  }

  if (error && !networkData) {
    return (
      <div className="app">
        <div className="error">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 Distributed Agent Networks</h1>
        <p>Day 19: Real-time Collaborative AI System</p>
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={activeTab === 'agents' ? 'active' : ''}
            onClick={() => setActiveTab('agents')}
          >
            Agent Monitor
          </button>
          <button 
            className={activeTab === 'network' ? 'active' : ''}
            onClick={() => setActiveTab('network')}
          >
            Network Status
          </button>
        </nav>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <Dashboard 
            networkData={networkData} 
            onSolveProblem={handleSolveProblem}
          />
        )}
        {activeTab === 'agents' && (
          <AgentMonitor agents={networkData?.agents || {}} />
        )}
        {activeTab === 'network' && (
          <NetworkStatus networkData={networkData} />
        )}
      </main>
    </div>
  );
}

export default App;
