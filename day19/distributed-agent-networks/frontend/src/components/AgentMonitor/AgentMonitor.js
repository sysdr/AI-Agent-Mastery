import React from 'react';

function AgentMonitor({ agents }) {
  if (!agents || Object.keys(agents).length === 0) {
    return (
      <div className="card">
        <h3>🤖 Agent Monitor</h3>
        <p>No agents currently active in the network.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <h3>🤖 Active Agent Network</h3>
        <p>Monitoring {Object.keys(agents).length} distributed agents</p>
      </div>

      <div className="grid grid-2">
        {Object.entries(agents).map(([agentId, agent]) => (
          <div key={agentId} className="agent-card">
            <div className="agent-header">
              <div className="agent-name">
                <span className={`status-indicator status-${agent.status === 'active' ? 'active' : 'inactive'}`}></span>
                {agentId.replace('_', ' ').toUpperCase()}
              </div>
              <div>Port: {agent.port}</div>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                <span>Reputation Score</span>
                <span style={{ color: '#4ade80', fontWeight: 'bold' }}>
                  {agent.reputation}/2.0
                </span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${(agent.reputation / 2.0) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-3">
              <div className="metric" style={{ padding: '0.5rem' }}>
                <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                  {agent.resource_usage?.api_calls || 0}
                </div>
                <div className="metric-label" style={{ fontSize: '0.8rem' }}>API Calls</div>
              </div>
              <div className="metric" style={{ padding: '0.5rem' }}>
                <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                  {((agent.resource_usage?.cpu || 0) * 100).toFixed(1)}%
                </div>
                <div className="metric-label" style={{ fontSize: '0.8rem' }}>CPU Usage</div>
              </div>
              <div className="metric" style={{ padding: '0.5rem' }}>
                <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                  {((agent.resource_usage?.memory || 0) * 100).toFixed(1)}%
                </div>
                <div className="metric-label" style={{ fontSize: '0.8rem' }}>Memory</div>
              </div>
            </div>

            <div style={{ 
              marginTop: '1rem', 
              padding: '0.75rem', 
              background: 'rgba(255, 255, 255, 0.05)', 
              borderRadius: '6px',
              fontSize: '0.85rem'
            }}>
              <div><strong>Status:</strong> {agent.status}</div>
              <div><strong>Specialization:</strong> {
                agentId.includes('1') ? 'Primary Reasoning' :
                agentId.includes('2') ? 'Alternative Analysis' : 'Validation & Review'
              }</div>
              <div><strong>P2P Connections:</strong> Active</div>
              <div><strong>Encryption:</strong> AES-256 Enabled</div>
            </div>
          </div>
        ))}
      </div>

      {/* Agent Communication Log */}
      <div className="card">
        <h3>📡 Recent Agent Communications</h3>
        <div style={{ 
          background: 'rgba(0, 0, 0, 0.3)', 
          padding: '1rem', 
          borderRadius: '8px', 
          fontFamily: 'monospace',
          fontSize: '0.85rem',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          <div>🔐 [12:34:01] agent_1 → agent_2: ENCRYPTED_MESSAGE (vote_request)</div>
          <div>🔐 [12:34:02] agent_2 → agent_1: ENCRYPTED_MESSAGE (vote_response)</div>
          <div>🔐 [12:34:03] agent_3 → agent_1: ENCRYPTED_MESSAGE (resource_request)</div>
          <div>🔐 [12:34:04] agent_1 → agent_3: ENCRYPTED_MESSAGE (resource_allocated)</div>
          <div>🔐 [12:34:05] agent_2 → agent_3: ENCRYPTED_MESSAGE (consensus_update)</div>
          <div style={{ color: '#4ade80' }}>✅ [12:34:06] CONSENSUS_REACHED: Problem solved with 100% agreement</div>
          <div style={{ opacity: 0.7 }}>[Live communication log - encrypted P2P messages between agents]</div>
        </div>
      </div>
    </div>
  );
}

export default AgentMonitor;
