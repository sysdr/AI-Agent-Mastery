import React, { useState, useEffect } from 'react';
import apiService from '../../services/apiService';

const SecurityMonitor = ({ onLogout }) => {
  const [securityData, setSecurityData] = useState({
    threats: [],
    blockedRequests: 0,
    suspiciousActivity: 0,
    lastScan: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      const data = await apiService.getSecurityData();
      setSecurityData(data);
    } catch (error) {
      console.error('Failed to fetch security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockThreat = async (threatId) => {
    try {
      await apiService.blockThreat(threatId);
      fetchSecurityData(); // Refresh data
    } catch (error) {
      console.error('Failed to block threat:', error);
    }
  };

  if (loading) {
    return (
      <div className="security-monitor">
        <div className="loading-spinner"></div>
        <p>Loading security data...</p>
      </div>
    );
  }

  return (
    <div className="security-monitor">
      <header className="security-header">
        <h1>Security Monitor</h1>
        <button onClick={onLogout} className="logout-btn">Logout</button>
      </header>

      <div className="security-stats">
        <div className="stat-card">
          <h3>Blocked Requests</h3>
          <div className="stat-value">{securityData.blockedRequests}</div>
        </div>
        <div className="stat-card">
          <h3>Suspicious Activity</h3>
          <div className="stat-value">{securityData.suspiciousActivity}</div>
        </div>
        <div className="stat-card">
          <h3>Last Scan</h3>
          <div className="stat-value">
            {securityData.lastScan ? new Date(securityData.lastScan).toLocaleTimeString() : 'Never'}
          </div>
        </div>
      </div>

      <div className="threats-section">
        <h2>Recent Threats</h2>
        {securityData.threats.length === 0 ? (
          <p className="no-threats">No threats detected</p>
        ) : (
          <div className="threats-list">
            {securityData.threats.map((threat) => (
              <div key={threat.id} className="threat-item">
                <div className="threat-info">
                  <h4>{threat.type}</h4>
                  <p>{threat.description}</p>
                  <span className="threat-time">{new Date(threat.timestamp).toLocaleString()}</span>
                </div>
                <div className="threat-actions">
                  <button 
                    onClick={() => handleBlockThreat(threat.id)}
                    className="block-btn"
                  >
                    Block
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityMonitor;
