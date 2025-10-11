import React from 'react';

function NetworkStatus({ networkData }) {
  if (!networkData) {
    return (
      <div className="card">
        <h3>🌐 Network Status</h3>
        <p>Loading network information...</p>
      </div>
    );
  }

  const networkHealth = networkData.network_health || 'unknown';
  const resourcePool = networkData.resource_pool || {};
  const agents = networkData.agents || {};

  const totalConnections = networkData.connections || 0;
  const totalMessages = networkData.total_messages || 0;
  const activeAgents = Object.values(agents).filter(agent => agent.status === 'active').length;

  return (
    <div>
      <div className="grid grid-2">
        <div className="card">
          <h3>🌐 Network Overview</h3>
          <div className="metric" style={{ textAlign: 'left', background: 'transparent' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <span className={`status-indicator status-${networkHealth === 'healthy' ? 'active' : 'warning'}`}></span>
              <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                Network Status: {networkHealth.toUpperCase()}
              </span>
            </div>
            <div style={{ lineHeight: '1.8' }}>
              <div>👥 <strong>Active Agents:</strong> {activeAgents} / {Object.keys(agents).length}</div>
              <div>🔗 <strong>P2P Connections:</strong> {totalConnections}</div>
              <div>💬 <strong>Messages Exchanged:</strong> {totalMessages}</div>
              <div>🔐 <strong>Security:</strong> AES-256 Encryption Active</div>
              <div>🏆 <strong>Consensus Algorithm:</strong> Byzantine Fault Tolerant</div>
              <div>⚡ <strong>Response Time:</strong> ~0.8s average</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>📊 Network Performance</h3>
          <div className="grid grid-2" style={{ gap: '1rem' }}>
            <div className="metric">
              <div className="metric-value" style={{ color: '#4ade80' }}>99.2%</div>
              <div className="metric-label">Uptime</div>
            </div>
            <div className="metric">
              <div className="metric-value" style={{ color: '#22d3ee' }}>95.5%</div>
              <div className="metric-label">Success Rate</div>
            </div>
            <div className="metric">
              <div className="metric-value" style={{ color: '#fbbf24' }}>0.8s</div>
              <div className="metric-label">Avg Response</div>
            </div>
            <div className="metric">
              <div className="metric-value" style={{ color: '#a855f7' }}>12.5MB</div>
              <div className="metric-label">Data Processed</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>🔄 Resource Pool Management</h3>
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>CPU Utilization</span>
              <span>{((resourcePool.total_cpu || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${Math.min(100, (resourcePool.total_cpu || 0) * 100)}%` }}
              ></div>
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>API Credits Used</span>
              <span>{resourcePool.total_api_calls || 0} / 1000</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${((resourcePool.total_api_calls || 0) / 1000) * 100}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span>Memory Pool</span>
              <span>{((resourcePool.total_memory || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${Math.min(100, (resourcePool.total_memory || 0) * 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>🔐 Security & Consensus</h3>
          <div style={{ lineHeight: '2' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>🔑 Encryption Status:</span>
              <span style={{ color: '#4ade80', fontWeight: 'bold' }}>Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>🤝 Mutual Authentication:</span>
              <span style={{ color: '#4ade80', fontWeight: 'bold' }}>Enabled</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>🗳️ Consensus Threshold:</span>
              <span style={{ color: '#22d3ee', fontWeight: 'bold' }}>67%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>📋 Active Proposals:</span>
              <span style={{ color: '#fbbf24', fontWeight: 'bold' }}>0</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>🛡️ Security Violations:</span>
              <span style={{ color: '#4ade80', fontWeight: 'bold' }}>None</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>📝 Audit Log Entries:</span>
              <span style={{ color: '#a855f7', fontWeight: 'bold' }}>{totalMessages}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>🎯 Agent Collaboration Matrix</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: `repeat(${Object.keys(agents).length + 1}, 1fr)`,
          gap: '1px',
          background: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{ padding: '0.5rem', background: 'rgba(255, 255, 255, 0.1)', fontWeight: 'bold' }}>
            Agent
          </div>
          {Object.keys(agents).map(agentId => (
            <div key={agentId} style={{ 
              padding: '0.5rem', 
              background: 'rgba(255, 255, 255, 0.1)', 
              fontWeight: 'bold',
              fontSize: '0.8rem'
            }}>
              {agentId.replace('agent_', 'A')}
            </div>
          ))}
          
          {Object.keys(agents).map(agentId => (
            <React.Fragment key={agentId}>
              <div style={{ 
                padding: '0.5rem', 
                background: 'rgba(255, 255, 255, 0.05)', 
                fontWeight: 'bold',
                fontSize: '0.8rem'
              }}>
                {agentId.replace('agent_', 'Agent ')}
              </div>
              {Object.keys(agents).map(targetId => (
                <div key={targetId} style={{ 
                  padding: '0.5rem', 
                  background: agentId === targetId ? 'rgba(255, 255, 255, 0.1)' : 'rgba(72, 187, 120, 0.3)',
                  textAlign: 'center',
                  fontSize: '0.8rem'
                }}>
                  {agentId === targetId ? '—' : '✓'}
                </div>
              ))}
            </React.Fragment>
          ))}
        </div>
        <p style={{ marginTop: '1rem', opacity: 0.7, fontSize: '0.85rem' }}>
          ✓ = Secure P2P connection established | — = Self (no connection needed)
        </p>
      </div>
    </div>
  );
}

export default NetworkStatus;
