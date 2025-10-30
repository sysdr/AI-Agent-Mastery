import React, { useState, useEffect } from 'react';
import { FiShield, FiAlertTriangle, FiCheck } from 'react-icons/fi';
import axios from 'axios';

const SecurityMonitor = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSecurityAlerts();
    const interval = setInterval(fetchSecurityAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityAlerts = async () => {
    try {
      const response = await axios.get('/security/alerts');
      setAlerts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch security alerts:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Security Monitoring</h1>
        <p>Real-time threat detection and security alerts</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <FiShield className="card-icon" />
            <h3>Security Alerts</h3>
          </div>
          {loading ? (
            <p>Loading security alerts...</p>
          ) : alerts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <FiCheck style={{ fontSize: '3rem', color: '#28a745' }} />
              <p>No active security threats detected</p>
            </div>
          ) : (
            <div>
              {alerts.map((alert, index) => (
                <div 
                  key={index} 
                  className={`alert-item alert-${alert.severity}`}
                >
                  <FiAlertTriangle style={{ marginRight: '10px' }} />
                  <div>
                    <strong>{alert.type}</strong>
                    <p>{alert.description}</p>
                    <small>{new Date(alert.timestamp * 1000).toLocaleString()}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SecurityMonitor;
