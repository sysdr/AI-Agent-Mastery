import React, { useState } from 'react';
import axios from 'axios';

const AgentRegistry = ({ onAgentRegistered }) => {
  const [agentId, setAgentId] = useState('');
  const [permissions, setPermissions] = useState(['read']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/auth/register', {
        agent_id: agentId,
        permissions: permissions
      });

      if (response.data.status === 'success') {
        onAgentRegistered(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const togglePermission = (permission) => {
    setPermissions(prev => 
      prev.includes(permission) 
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    );
  };

  return (
    <div className="agent-registry">
      <h2>🤖 Agent Registration</h2>
      <p>Register your agent to join the secure communication network</p>

      <form onSubmit={handleRegister} className="registration-form">
        <div className="form-group">
          <label htmlFor="agentId">Agent ID:</label>
          <input
            type="text"
            id="agentId"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            placeholder="e.g., agent-001"
            required
          />
        </div>

        <div className="form-group">
          <label>Permissions:</label>
          <div className="permissions-grid">
            {['read', 'write', 'admin', 'monitor'].map(permission => (
              <label key={permission} className="permission-checkbox">
                <input
                  type="checkbox"
                  checked={permissions.includes(permission)}
                  onChange={() => togglePermission(permission)}
                />
                {permission}
              </label>
            ))}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading || !agentId} className="register-btn">
          {loading ? 'Registering...' : 'Register Agent'}
        </button>
      </form>

      <div className="security-features">
        <h3>🔐 Security Features</h3>
        <ul>
          <li>End-to-end encryption with AES-256</li>
          <li>JWT-based authentication with 15-minute expiry</li>
          <li>Real-time threat monitoring with Gemini AI</li>
          <li>Comprehensive audit logging</li>
          <li>Mutual TLS for agent-to-agent communication</li>
        </ul>
      </div>
    </div>
  );
};

export default AgentRegistry;
