import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

function Dashboard({ networkData, onSolveProblem }) {
  const [problemText, setProblemText] = useState('');
  const [solving, setSolving] = useState(false);
  const [solution, setSolution] = useState(null);

  const handleSolveProblem = async () => {
    if (!problemText.trim()) return;
    
    setSolving(true);
    try {
      const result = await onSolveProblem(problemText);
      setSolution(result);
    } catch (error) {
      console.error('Failed to solve problem:', error);
    } finally {
      setSolving(false);
    }
  };

  const agentData = networkData?.agents ? Object.entries(networkData.agents).map(([id, agent]) => ({
    name: id.replace('agent_', 'Agent '),
    reputation: agent.reputation,
    apiCalls: agent.resource_usage?.api_calls || 0,
    cpu: (agent.resource_usage?.cpu || 0) * 100
  })) : [];

  const networkHealth = networkData?.network_health || 'unknown';
  const resourcePool = networkData?.resource_pool || {};

  return (
    <div className="dashboard">
      {/* Network Overview */}
      <div className="grid grid-4">
        <div className="card metric">
          <div className="metric-value">{Object.keys(networkData?.agents || {}).length}</div>
          <div className="metric-label">Active Agents</div>
        </div>
        <div className="card metric">
          <div className="metric-value">{networkData?.connections || 0}</div>
          <div className="metric-label">P2P Connections</div>
        </div>
        <div className="card metric">
          <div className="metric-value">{networkData?.total_messages || 0}</div>
          <div className="metric-label">Messages Sent</div>
        </div>
        <div className="card metric">
          <div className="metric-value">
            <span className={`status-indicator status-${networkHealth === 'healthy' ? 'active' : 'warning'}`}></span>
            {networkHealth}
          </div>
          <div className="metric-label">Network Health</div>
        </div>
      </div>

      {/* Problem Solving Interface */}
      <div className="card">
        <h3>🧠 Collaborative Problem Solving</h3>
        <div className="input-group">
          <label>Enter a problem for the agent network to solve:</label>
          <textarea
            value={problemText}
            onChange={(e) => setProblemText(e.target.value)}
            placeholder="e.g., What are the key factors for successful distributed systems?"
            rows="3"
          />
        </div>
        <button 
          className="button" 
          onClick={handleSolveProblem}
          disabled={solving || !problemText.trim()}
        >
          {solving ? '🤔 Agents Collaborating...' : '🚀 Solve with Network'}
        </button>
        
        {solution && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(72, 187, 120, 0.1)', borderRadius: '8px', border: '1px solid rgba(72, 187, 120, 0.3)' }}>
            <h4>✅ Consensus Solution</h4>
            <p><strong>Problem:</strong> {solution.problem}</p>
            <p><strong>Solution:</strong> {solution.consensus_solution}</p>
            <p><strong>Confidence:</strong> {(solution.confidence * 100).toFixed(1)}%</p>
            <p><strong>Participating Agents:</strong> {solution.participating_agents}</p>
            
            {solution.individual_solutions && (
              <details style={{ marginTop: '1rem' }}>
                <summary>View Individual Agent Solutions</summary>
                <div style={{ marginTop: '0.5rem' }}>
                  {solution.individual_solutions.map((sol, idx) => (
                    <div key={idx} style={{ margin: '0.5rem 0', padding: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px' }}>
                      <strong>{sol.agent_id}:</strong> {sol.solution}
                      <br />
                      <small>Confidence: {(sol.confidence * 100).toFixed(1)}%, Time: {sol.processing_time.toFixed(2)}s</small>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </div>

      {/* Agent Performance Chart */}
      <div className="grid grid-2">
        <div className="card">
          <h3>📊 Agent Reputation Scores</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={agentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
              <YAxis stroke="rgba(255,255,255,0.7)" />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(0,0,0,0.8)', 
                  border: '1px solid rgba(255,255,255,0.2)', 
                  borderRadius: '8px' 
                }} 
              />
              <Bar dataKey="reputation" fill="#4ade80" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>🔄 Resource Usage</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={agentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
              <YAxis stroke="rgba(255,255,255,0.7)" />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(0,0,0,0.8)', 
                  border: '1px solid rgba(255,255,255,0.2)', 
                  borderRadius: '8px' 
                }} 
              />
              <Line type="monotone" dataKey="apiCalls" stroke="#fbbf24" strokeWidth={2} />
              <Line type="monotone" dataKey="cpu" stroke="#22d3ee" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Resource Pool Status */}
      <div className="card">
        <h3>💾 Resource Pool Status</h3>
        <div className="grid grid-3">
          <div className="metric">
            <div className="metric-value">{resourcePool.total_cpu?.toFixed(2) || '0.00'}</div>
            <div className="metric-label">Total CPU Usage</div>
          </div>
          <div className="metric">
            <div className="metric-value">{resourcePool.total_api_calls || 0}</div>
            <div className="metric-label">API Calls Made</div>
          </div>
          <div className="metric">
            <div className="metric-value">{resourcePool.available_api_credits || 0}</div>
            <div className="metric-label">Available Credits</div>
          </div>
        </div>
        
        <div style={{ marginTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>API Credits Usage</span>
            <span>{((1000 - (resourcePool.available_api_credits || 1000)) / 10).toFixed(1)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((1000 - (resourcePool.available_api_credits || 1000)) / 1000) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
