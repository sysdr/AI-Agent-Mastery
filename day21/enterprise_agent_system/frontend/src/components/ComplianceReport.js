import React, { useState, useEffect } from 'react';
import { FiCheckCircle, FiFileText } from 'react-icons/fi';
import axios from 'axios';

const ComplianceReport = () => {
  const [auditTrail, setAuditTrail] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditTrail();
  }, []);

  const fetchAuditTrail = async () => {
    try {
      const response = await axios.get('/compliance/audit-trail');
      setAuditTrail(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch audit trail:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Compliance & Audit</h1>
        <p>Regulatory compliance monitoring and audit trails</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card" style={{ gridColumn: 'span 2' }}>
          <div className="card-header">
            <FiFileText className="card-icon" />
            <h3>Audit Trail</h3>
          </div>
          {loading ? (
            <p>Loading audit trail...</p>
          ) : (
            <div className="activity-log">
              {auditTrail.length === 0 ? (
                <p>No audit entries found</p>
              ) : (
                auditTrail.map((entry, index) => (
                  <div key={index} className="log-entry">
                    <div>
                      <strong>{entry.event_type}</strong> - {entry.task_type}
                    </div>
                    <div>Agent: {entry.agent} | Status: {entry.status}</div>
                    <div className="log-timestamp">
                      {new Date(entry.timestamp * 1000).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComplianceReport;
