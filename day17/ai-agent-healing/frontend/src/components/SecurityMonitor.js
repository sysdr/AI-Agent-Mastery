import React, { useState, useEffect } from 'react';

const SecurityMonitor = () => {
  const [securityStatus, setSecurityStatus] = useState(null);
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      const [statusRes, incidentsRes] = await Promise.all([
        fetch('http://localhost:8000/security/status'),
        fetch('http://localhost:8000/incidents')
      ]);
      
      const statusData = await statusRes.json();
      const incidentsData = await incidentsRes.json();
      
      setSecurityStatus(statusData);
      setIncidents(incidentsData);
    } catch (error) {
      console.error('Failed to fetch security data:', error);
    }
  };

  const simulateAttack = async (attackType) => {
    try {
      const response = await fetch(`/simulate/attack?attack_type=${attackType}`, {
        method: 'POST'
      });
      const data = await response.json();
      alert(`Attack simulated: ${data.incident_id}`);
      setTimeout(fetchSecurityData, 2000); // Refresh after 2 seconds
    } catch (error) {
      console.error('Failed to simulate attack:', error);
    }
  };

  const getThreatColor = (level) => {
    switch(level) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#F97316';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'low': return '🟢';
      case 'medium': return '🟡';
      case 'high': return '🟠';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  if (!securityStatus) {
    return <div className="loading">Loading security data...</div>;
  }

  return (
    <div className="security-monitor">
      <div className="security-overview">
        <div className="security-card">
          <h3>🛡️ Threat Level</h3>
          <div 
            className="threat-level"
            style={{ color: getThreatColor(securityStatus.threat_level) }}
          >
            {securityStatus.threat_level.toUpperCase()}
          </div>
        </div>

        <div className="security-card">
          <h3>🚨 Active Incidents</h3>
          <div className="metric-value">
            {securityStatus.active_incidents}
          </div>
        </div>

        <div className="security-card">
          <h3>🕐 Last Attack</h3>
          <div className="last-attack">
            {securityStatus.last_attack 
              ? new Date(securityStatus.last_attack).toLocaleString()
              : 'None detected'
            }
          </div>
        </div>

        <div className="security-card">
          <h3>🔄 Last Updated</h3>
          <div className="last-updated">
            {securityStatus.last_updated 
              ? new Date(securityStatus.last_updated).toLocaleString()
              : 'Never'
            }
          </div>
        </div>
      </div>

      <div className="attack-simulation">
        <h3>🧪 Attack Simulation (Testing Only)</h3>
        <div className="simulation-buttons">
          <button 
            className="sim-button ddos"
            onClick={() => simulateAttack('ddos')}
          >
            💥 DDoS Attack
          </button>
          <button 
            className="sim-button brute-force"
            onClick={() => simulateAttack('brute_force')}
          >
            🔓 Brute Force
          </button>
          <button 
            className="sim-button malware"
            onClick={() => simulateAttack('malware')}
          >
            🦠 Malware
          </button>
          <button 
            className="sim-button data-breach"
            onClick={() => simulateAttack('data_breach')}
          >
            📊 Data Breach
          </button>
        </div>
      </div>

      {incidents.length > 0 && (
        <div className="recent-incidents">
          <h3>📋 Recent Security Incidents</h3>
          <div className="incidents-list">
            {incidents.slice(0, 10).map((incident, index) => (
              <div key={index} className={`incident-item severity-${incident.severity}`}>
                <div className="incident-header">
                  <span className="severity-icon">
                    {getSeverityIcon(incident.severity)}
                  </span>
                  <span className="incident-id">{incident.id}</span>
                  <span className="incident-type">{incident.type.replace('_', ' ').toUpperCase()}</span>
                  <span className={`incident-status status-${incident.status}`}>
                    {incident.status.toUpperCase()}
                  </span>
                </div>
                <div className="incident-details">
                  <div className="incident-time">
                    {new Date(incident.created_at).toLocaleString()}
                  </div>
                  {incident.response_actions.length > 0 && (
                    <div className="response-actions">
                      <strong>Response Actions:</strong>
                      <ul>
                        {incident.response_actions.slice(0, 3).map((action, idx) => (
                          <li key={idx}>
                            ✅ {action.action.replace('_', ' ')}
                          </li>
                        ))}
                        {incident.response_actions.length > 3 && (
                          <li>... and {incident.response_actions.length - 3} more</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityMonitor;
