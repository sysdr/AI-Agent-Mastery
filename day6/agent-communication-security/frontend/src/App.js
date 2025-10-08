import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SecurityDashboard from './components/SecurityDashboard';
import AgentRegistry from './components/AgentRegistry';
import MessageInterface from './components/MessageInterface';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [currentAgent, setCurrentAgent] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('agent_token'));
  const [activeTab, setActiveTab] = useState('register');

  useEffect(() => {
    if (token) {
      // Verify token validity
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const handleAgentRegistration = (agentData) => {
    setCurrentAgent(agentData.agent_id);
    setToken(agentData.token);
    localStorage.setItem('agent_token', agentData.token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${agentData.token}`;
    setActiveTab('messages');
  };

  const handleLogout = () => {
    setCurrentAgent(null);
    setToken(null);
    localStorage.removeItem('agent_token');
    delete axios.defaults.headers.common['Authorization'];
    setActiveTab('register');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🔐 Agent Communication Security System</h1>
        {currentAgent && (
          <div className="agent-info">
            <span>Agent: {currentAgent}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        )}
      </header>

      <nav className="app-nav">
        <button 
          className={activeTab === 'register' ? 'active' : ''}
          onClick={() => setActiveTab('register')}
        >
          Agent Registry
        </button>
        {currentAgent && (
          <>
            <button 
              className={activeTab === 'messages' ? 'active' : ''}
              onClick={() => setActiveTab('messages')}
            >
              Secure Messages
            </button>
            <button 
              className={activeTab === 'dashboard' ? 'active' : ''}
              onClick={() => setActiveTab('dashboard')}
            >
              Security Dashboard
            </button>
          </>
        )}
      </nav>

      <main className="app-main">
        {activeTab === 'register' && (
          <AgentRegistry onAgentRegistered={handleAgentRegistration} />
        )}
        {activeTab === 'messages' && currentAgent && (
          <MessageInterface currentAgent={currentAgent} />
        )}
        {activeTab === 'dashboard' && currentAgent && (
          <SecurityDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
