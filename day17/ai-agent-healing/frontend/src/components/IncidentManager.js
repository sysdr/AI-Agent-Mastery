import React, { useState, useEffect } from 'react';

const IncidentManager = () => {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await fetch('http://localhost:8000/incidents');
      const data = await response.json();
      setIncidents(data);
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#F97316';
      case 'critical': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'active': return '🟡';
      case 'resolved': return '✅';
      case 'investigating': return '🔍';
      default: return '❓';
    }
  };

  const formatDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end - start) / 1000); // seconds
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  return (
    <div className="incident-manager">
      <div className="incidents-summary">
        <div className="summary-card">
          <h3>📊 Incidents Summary</h3>
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Total:</span>
              <span className="stat-value">{incidents.length}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Active:</span>
              <span className="stat-value">
                {incidents.filter(i => i.status === 'active').length}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Resolved:</span>
              <span className="stat-value">
                {incidents.filter(i => i.status === 'resolved').length}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="incidents-content">
        <div className="incidents-list">
          <h3>🚨 All Incidents</h3>
          {incidents.length === 0 ? (
            <div className="no-incidents">
              <p>🎉 No security incidents detected!</p>
              <p>Your AI agent system is running smoothly.</p>
            </div>
          ) : (
            <div className="incidents-table">
              {incidents.map((incident, index) => (
                <div 
                  key={index} 
                  className={`incident-row ${selectedIncident?.id === incident.id ? 'selected' : ''}`}
                  onClick={() => setSelectedIncident(incident)}
                >
                  <div className="incident-basic-info">
                    <div className="incident-status">
                      {getStatusIcon(incident.status)}
                    </div>
                    <div className="incident-id">{incident.id}</div>
                    <div className="incident-type">
                      {incident.type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div 
                      className="incident-severity"
                      style={{ color: getSeverityColor(incident.severity) }}
                    >
                      {incident.severity.toUpperCase()}
                    </div>
                    <div className="incident-duration">
                      {formatDuration(incident.created_at, incident.resolved_at)}
                    </div>
                    <div className="incident-time">
                      {new Date(incident.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedIncident && (
          <div className="incident-details">
            <h3>🔍 Incident Details</h3>
            <div className="detail-card">
              <div className="detail-header">
                <h4>{selectedIncident.id}</h4>
                <div 
                  className="detail-severity"
                  style={{ color: getSeverityColor(selectedIncident.severity) }}
                >
                  {selectedIncident.severity.toUpperCase()} SEVERITY
                </div>
              </div>
              
              <div className="detail-info">
                <div className="info-row">
                  <span className="info-label">Type:</span>
                  <span className="info-value">
                    {selectedIncident.type.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Status:</span>
                  <span className="info-value">
                    {getStatusIcon(selectedIncident.status)} {selectedIncident.status.toUpperCase()}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Created:</span>
                  <span className="info-value">
                    {new Date(selectedIncident.created_at).toLocaleString()}
                  </span>
                </div>
                {selectedIncident.resolved_at && (
                  <div className="info-row">
                    <span className="info-label">Resolved:</span>
                    <span className="info-value">
                      {new Date(selectedIncident.resolved_at).toLocaleString()}
                    </span>
                  </div>
                )}
                <div className="info-row">
                  <span className="info-label">Duration:</span>
                  <span className="info-value">
                    {formatDuration(selectedIncident.created_at, selectedIncident.resolved_at)}
                  </span>
                </div>
              </div>

              {selectedIncident.details && (
                <div className="incident-specific-details">
                  <h5>📋 Incident Details</h5>
                  <div className="details-content">
                    {Object.entries(selectedIncident.details).map(([key, value]) => (
                      <div key={key} className="detail-item">
                        <span className="detail-key">
                          {key.replace('_', ' ').toUpperCase()}:
                        </span>
                        <span className="detail-value">
                          {Array.isArray(value) ? value.join(', ') : value.toString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedIncident.response_actions && selectedIncident.response_actions.length > 0 && (
                <div className="response-actions-detail">
                  <h5>⚡ Response Actions</h5>
                  <div className="actions-timeline">
                    {selectedIncident.response_actions.map((action, index) => (
                      <div key={index} className="action-item">
                        <div className="action-status">
                          {action.status === 'completed' ? '✅' : '⏳'}
                        </div>
                        <div className="action-description">
                          {action.action.replace('_', ' ')}
                        </div>
                        <div className="action-time">
                          {new Date(action.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IncidentManager;
