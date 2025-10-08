import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

// Configure axios defaults for authentication
axios.defaults.headers.common['Authorization'] = 'Bearer demo_token';

function App() {
  const [workflows, setWorkflows] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSystemStatus();
    fetchWorkflows();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/system/status`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/workflows`);
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    }
  };

  const createWorkflow = async () => {
    setLoading(true);
    try {
      const workflowData = {
        workflow_type: 'customer_onboarding',
        customer_id: `CUST_${Date.now()}`,
        data: {
          documents: [
            { id: 'doc1', type: 'identity', name: 'passport.pdf' },
            { id: 'doc2', type: 'financial', name: 'bank_statement.pdf' }
          ],
          consent_granted: true,
          data_purpose: 'account_opening'
        },
        compliance_level: 'standard'
      };

      await axios.post(`${API_BASE}/api/workflows`, workflowData);
      await fetchWorkflows();
    } catch (error) {
      console.error('Failed to create workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🔧 Production Orchestration Dashboard</h1>
        <p>AI Agent Coordination with Security & Compliance</p>
      </header>

      <main className="dashboard">
        <section className="system-status">
          <h2>System Status</h2>
          <div className="status-grid">
            <div className="status-card">
              <h3>Overall Status</h3>
              <span className={`status-indicator ${systemStatus.status}`}>
                {systemStatus.status || 'Unknown'}
              </span>
            </div>
            <div className="status-card">
              <h3>Active Workflows</h3>
              <span className="metric">{systemStatus.active_workflows || 0}</span>
            </div>
            <div className="status-card">
              <h3>Agent Health</h3>
              <div className="agent-status">
                {systemStatus.agent_status && Object.entries(systemStatus.agent_status).map(([agent, status]) => (
                  <div key={agent} className="agent-item">
                    <span className={`agent-indicator ${status}`}></span>
                    {agent.replace('_', ' ')}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="workflow-management">
          <div className="section-header">
            <h2>Workflow Management</h2>
            <button 
              onClick={createWorkflow} 
              disabled={loading}
              className="create-workflow-btn"
            >
              {loading ? '⏳ Creating...' : '🚀 Create Onboarding Workflow'}
            </button>
          </div>

          <div className="workflows-list">
            {workflows.map(workflow => (
              <div key={workflow.workflow_id} className="workflow-card">
                <div className="workflow-header">
                  <h3>Workflow: {workflow.workflow_id.slice(0, 8)}...</h3>
                  <span className={`workflow-status ${workflow.status}`}>
                    {workflow.status}
                  </span>
                </div>
                
                <div className="workflow-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{width: `${workflow.progress}%`}}
                    ></div>
                  </div>
                  <span className="progress-text">{workflow.progress.toFixed(1)}%</span>
                </div>

                <div className="workflow-details">
                  <p><strong>Created:</strong> {new Date(workflow.created_at * 1000).toLocaleString()}</p>
                  <p><strong>Updated:</strong> {new Date(workflow.updated_at * 1000).toLocaleString()}</p>
                  
                  {workflow.results && workflow.results.steps && (
                    <div className="workflow-steps">
                      <h4>Processing Steps:</h4>
                      <ul>
                        {workflow.results.steps.map((step, index) => (
                          <li key={index} className="step-item">
                            <span className="step-name">{step.step.replace('_', ' ')}</span>
                            <span className={`step-status ${step.result ? 'success' : 'pending'}`}>
                              {step.result ? '✅' : '⏳'}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {workflows.length === 0 && (
              <div className="empty-state">
                <h3>No workflows yet</h3>
                <p>Create your first customer onboarding workflow to see orchestration in action!</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
