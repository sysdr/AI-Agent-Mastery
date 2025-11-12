import React, { useState } from 'react';
import { Send, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

const IntegrationPanel = () => {
  const [customerId, setCustomerId] = useState('CUST001');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [updateData, setUpdateData] = useState({
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@example.com',
    active: true
  });

  const handleQuery = async () => {
    setLoading(true);
    try {
      const data = await api.getCustomer(customerId);
      setResult({ type: 'query', data });
    } catch (error) {
      setResult({ type: 'error', data: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const data = await api.updateCustomer(customerId, updateData);
      setResult({ type: 'update', data });
    } catch (error) {
      setResult({ type: 'error', data: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="integration-panel">
      <div className="panel-grid">
        <div className="panel-card">
          <h3>Query Customer Data</h3>
          <div className="form-group">
            <label>Customer ID</label>
            <input
              type="text"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              placeholder="Enter customer ID"
            />
          </div>
          <button className="btn primary" onClick={handleQuery} disabled={loading}>
            <Send size={16} />
            Query Legacy System
          </button>
        </div>

        <div className="panel-card">
          <h3>Update Customer Data</h3>
          <div className="form-group">
            <label>First Name</label>
            <input
              type="text"
              value={updateData.firstName}
              onChange={(e) => setUpdateData({...updateData, firstName: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Last Name</label>
            <input
              type="text"
              value={updateData.lastName}
              onChange={(e) => setUpdateData({...updateData, lastName: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={updateData.email}
              onChange={(e) => setUpdateData({...updateData, email: e.target.value})}
            />
          </div>
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={updateData.active}
                onChange={(e) => setUpdateData({...updateData, active: e.target.checked})}
              />
              Active
            </label>
          </div>
          <button className="btn success" onClick={handleUpdate} disabled={loading}>
            <RefreshCw size={16} />
            Update via Integration
          </button>
        </div>
      </div>

      {result && (
        <div className={`result-card ${result.type}`}>
          <h3>Integration Result</h3>
          <pre>{JSON.stringify(result.data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default IntegrationPanel;
